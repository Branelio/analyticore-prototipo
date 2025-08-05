from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware # <-- NUEVA IMPORTACIÓN
from pydantic import BaseModel
import uuid
import os
from sqlalchemy import create_engine, Column, String, Text, Uuid, DateTime, ARRAY
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import requests

# --- 1. Configuración de variables de entorno ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada")

JAVA_SERVICE_URL = os.getenv("JAVA_SERVICE_URL")
if not JAVA_SERVICE_URL:
    JAVA_SERVICE_URL = "http://localhost:8080" 

# --- 2. Configuración de la base de datos ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 3. Modelo de la tabla `jobs` ---
class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text_to_analyze = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    sentiment = Column(String(10))
    keywords = Column(ARRAY(Text))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Crea la tabla en la base de datos
Base.metadata.create_all(bind=engine)

# --- 4. Inicialización de la aplicación FastAPI ---
app = FastAPI()

# --- Habilitar CORS para permitir peticiones desde el frontend ---
origins = [
    "https://analyticore-frontend-xmp0.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función para la inyección de dependencias de la sesión de la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 5. Esquemas de Pydantic para la validación ---
class TextSubmission(BaseModel):
    text: str

class JobStatusResponse(BaseModel):
    job_id: uuid.UUID
    status: str
    sentiment: str = None
    keywords: list[str] = None

# --- 6. Endpoints de la API ---

@app.get("/")
def read_root():
    return {"message": "¡Servicio de Python operativo y listo para recibir peticiones!"}

@app.post("/submit_job")
def submit_job(submission: TextSubmission, db: Session = Depends(get_db)):
    try:
        if not submission.text:
            raise HTTPException(status_code=400, detail="El texto no puede estar vacío")

        new_job = Job(text_to_analyze=submission.text)
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        job_id_str = str(new_job.job_id)

        try:
            response = requests.post(
                f"{JAVA_SERVICE_URL}/analyze",
                json={"jobId": job_id_str}
            )
            response.raise_for_status()
            print(f"Solicitud de análisis enviada para el trabajo {job_id_str}")
        except requests.exceptions.RequestException as e:
            new_job.status = "ERROR"
            db.commit()
            raise HTTPException(status_code=500, detail=f"Error al llamar al servicio de análisis: {e}")

        return {"job_id": new_job.job_id, "status": new_job.status}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {e}")

@app.get("/job_status/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Trabajo no encontrado")
        
        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            sentiment=job.sentiment,
            keywords=job.keywords
        )
    finally:
        pass
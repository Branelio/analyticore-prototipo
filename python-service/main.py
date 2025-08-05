from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import os
from sqlalchemy import create_engine, Column, String, Text, Uuid, DateTime, ARRAY
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import requests # <-- NUEVA IMPORTACIÓN

# --- 1. Configuración de la base de datos ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- NUEVA VARIABLE DE ENTORNO para el servicio de Java ---
JAVA_SERVICE_URL = os.getenv("JAVA_SERVICE_URL")
if not JAVA_SERVICE_URL:
    # Esto es para desarrollo local, en Render se usará la URL de la variable de entorno
    JAVA_SERVICE_URL = "http://localhost:8080" 

# --- 2. Modelo de la tabla `jobs` ---
class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text_to_analyze = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    sentiment = Column(String(10))
    keywords = Column(ARRAY(Text))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Crea la tabla en la base de datos (se ejecutará al iniciar el servicio)
Base.metadata.create_all(bind=engine)

# --- 3. Inicialización de la aplicación FastAPI ---
app = FastAPI()

# --- 4. Esquemas de Pydantic para la validación ---
class TextSubmission(BaseModel):
    text: str

class JobStatusResponse(BaseModel):
    job_id: uuid.UUID
    status: str
    sentiment: str = None
    keywords: list[str] = None

# --- 5. Endpoints de la API ---

@app.post("/submit_job")
def submit_job(submission: TextSubmission):
    db = SessionLocal()
    try:
        if not submission.text:
            raise HTTPException(status_code=400, detail="El texto no puede estar vacío")

        # 1. Crea el registro en la base de datos
        new_job = Job(text_to_analyze=submission.text)
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        job_id_str = str(new_job.job_id)

        # 2. Llama al servicio de Java para iniciar el análisis # <-- CÓDIGO NUEVO
        try:
            response = requests.post(
                f"{JAVA_SERVICE_URL}/analyze",
                json={"jobId": job_id_str}
            )
            response.raise_for_status() # Lanza un error si el status code no es 2xx
            print(f"Solicitud de análisis enviada para el trabajo {job_id_str}")
        except requests.exceptions.RequestException as e:
            # Si el servicio de Java falla, actualizamos el estado del trabajo a ERROR
            new_job.status = "ERROR"
            db.commit()
            raise HTTPException(status_code=500, detail=f"Error al llamar al servicio de análisis: {e}")

        return {"job_id": new_job.job_id, "status": new_job.status}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {e}")
    finally:
        db.close()

@app.get("/job_status/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: uuid.UUID):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Trabajo no encontrado")
        
        # Mapea el resultado para que coincida con el modelo de respuesta
        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            sentiment=job.sentiment,
            keywords=job.keywords
        )
    finally:
        db.close()
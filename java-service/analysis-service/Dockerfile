# ---- Etapa 1: Build ----
# Usa una imagen base de Maven con OpenJDK 17 para compilar la aplicación.
FROM maven:3.8.5-openjdk-17 AS build

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copia el archivo pom.xml y las fuentes del proyecto.
COPY pom.xml .
COPY src ./src

# Compila la aplicación, saltando las pruebas para acelerar el proceso.
RUN mvn clean package -DskipTests

# ---- Etapa 2: Ejecución ----
# Usa una imagen base más ligera para la ejecución de la aplicación.
FROM openjdk:17-jdk-slim

# Establece el directorio de trabajo.
WORKDIR /app

# Copia el archivo .jar compilado desde la etapa de build a esta imagen.
COPY --from=build /app/target/*.jar app.jar

# Expone el puerto por defecto de Spring Boot.
EXPOSE 8080

# Comando para iniciar la aplicación.
CMD ["java", "-jar", "app.jar"]
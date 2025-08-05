# ---- Etapa 1: Build de la aplicación React ----
# Usa la imagen oficial de Node para construir la aplicación.
FROM node:20 AS build

# Establece el directorio de trabajo.
WORKDIR /app

# Copia los archivos de configuración y dependencias.
COPY package.json ./
COPY package-lock.json ./

# Instala las dependencias.
RUN npm install

# Copia el código fuente de la aplicación.
COPY . .

# Construye la aplicación para producción.
RUN npm run build

# ---- Etapa 2: Servir la aplicación con Nginx ----
# Usa una imagen ligera de Nginx.
FROM nginx:stable-alpine

# Copia la configuración de Nginx.
# (Necesitarías crear un archivo nginx.conf en la carpeta frontend).
# Para el prototipo, usaremos una configuración predeterminada.

# Copia los archivos estáticos de la aplicación desde la etapa de build.
COPY --from=build /app/build /usr/share/nginx/html

# Expone el puerto 80, que es el puerto predeterminado de Nginx.
EXPOSE 80

# Comando para iniciar Nginx.
CMD ["nginx", "-g", "daemon off;"]
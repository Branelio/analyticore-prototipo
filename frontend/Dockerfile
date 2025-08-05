# ---- Etapa 1: Build de la aplicación React ----
FROM node:20 AS build

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./

RUN npm install

COPY . .

# --- CORRECCIÓN ---
# Aquí se define y pasa la variable de entorno REACT_APP_API_BASE_URL
# 'ARG' la hace disponible en la etapa de build, y 'ENV' la usa.
ARG REACT_APP_API_BASE_URL
ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL
# --- FIN DE LA CORRECCIÓN ---

RUN npm run build

# ---- Etapa 2: Servir la aplicación con Nginx ----
FROM nginx:stable-alpine

COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
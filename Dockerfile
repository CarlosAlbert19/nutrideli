# Version de python
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo requirements.txt 
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación en el contenedor
COPY . .

# Exponer el puerto en el que tu aplicación correrá (Flask generalmente usa el 5000)
EXPOSE 5000

# Configurar la variable de entorno para Flask
ENV FLASK_ENV=production

# Comando para correr tu aplicación
CMD ["flask", "run", "--host=0.0.0.0"]

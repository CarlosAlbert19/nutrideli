# Version de python
FROM python:3.12

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo requirements.txt
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación en el contenedor
COPY . .

# Crear el directorio para la base de datos
RUN mkdir -p /app/instance && chmod -R 777 /app/instance

# Exponer el puerto en el que tu aplicación correrá (Flask generalmente usa el 5000)
EXPOSE 5000

# Configurar la variable de entorno para Flask
ENV FLASK_ENV=development
ENV FLASK_APP=run.py
ENV SECRET_KEY=260fa31c72684ad278f65cac9702
ENV SQLALCHEMY_DATABASE_URI=sqlite:///app/instance/site.db

# Comando para correr tu aplicación
CMD ["flask", "run", "--host=0.0.0.0"]


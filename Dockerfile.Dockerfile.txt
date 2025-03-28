FROM python:3.12-slim
WORKDIR /app
COPY app.py .
# Si decides no incluir el archivo de credenciales en el repositorio, omite la línea siguiente.
# COPY service_account.json .
RUN pip install flask pandas openpyxl google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
EXPOSE 8080
CMD ["python3", "app.py"]

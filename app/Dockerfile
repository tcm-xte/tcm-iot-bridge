# Base Image
FROM python:3.11-slim

WORKDIR /app
COPY . .

# Install Despendencies
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

# Expoze implicit port 
ENV PORT=8080
#CMD ["python", "main.py"]
CMD ["gunicorn", "--bind", ":8080", "main:app"]

FROM python:3.11-slim
WORKDIR /app
COPY requirements.in .
RUN pip install --no-cache-dir -r requirements.in
COPY . .
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]

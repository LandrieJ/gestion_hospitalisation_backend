
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

COPY . .

EXPOSE 8000

CMD ["gunicorn", "gestion_hospitalisation.wsgi:application", "--bind", "0.0.0.0:8000"]

FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p static
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Debug: Test if gunicorn can start and show errors
CMD ["sh", "-c", "python -c \"import gunicorn; print('Gunicorn imported successfully')\" && python -c \"from surveillance_core.wsgi import application; print('WSGI application imported successfully')\" && echo 'Starting gunicorn...' && exec python -m gunicorn surveillance_core.wsgi:application --bind 0.0.0.0:8000 --workers 1 --access-logfile - --error-logfile -"]
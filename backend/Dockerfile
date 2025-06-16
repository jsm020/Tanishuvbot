FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# backend papkasini va manage.py ni alohida nusxalash
COPY backend/ ./backend/
COPY manage.py ./

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && supervisord -c supervisord.conf"]

FROM python:3.12-slim

# Kerakli tizim paketlarini o‘rnatish
RUN apt-get update && apt-get install -y supervisor && apt-get clean

# Loyihaning ishchi katalogi
WORKDIR /app

# Python kutubxonalarini o‘rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Boshqa barcha fayllarni nusxalash
COPY . .

# Loglar buferlanmasin
ENV PYTHONUNBUFFERED=1

# Komanda: migrate + static + supervisor
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && supervisord -c supervisord.conf"]

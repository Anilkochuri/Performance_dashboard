# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Optional system deps for matplotlib/reportlab (fonts, png)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libfreetype6-dev libpng-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app/

# Default port; platforms like Render/Northflank will override or map it
ENV PORT=10000

CMD ["gunicorn", "--workers", "3", "--threads", "8", "--timeout", "120", "-b", "0.0.0.0:10000", "app:app"]

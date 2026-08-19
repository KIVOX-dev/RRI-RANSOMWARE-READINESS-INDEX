FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# WeasyPrint runtime deps (pango/cairo/gdk-pixbuf) + fonts for PDF rendering.
# Package name for gdk-pixbuf varies by Debian release (libgdk-pixbuf2.0-0 on
# bookworm, libgdk-pixbuf-2.0-0 on trixie+), so try both.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
    libffi-dev shared-mime-info fonts-dejavu-core curl \
    && (apt-get install -y --no-install-recommends libgdk-pixbuf-2.0-0 \
        || apt-get install -y --no-install-recommends libgdk-pixbuf2.0-0) \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

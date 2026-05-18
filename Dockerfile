FROM python:3.10-alpine
RUN pip install --no-cache-dir cloudscraper
COPY flare-adapter.py /app/
CMD ["python", "/app/flare-adapter.py"]

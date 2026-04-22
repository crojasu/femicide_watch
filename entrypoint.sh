#!/bin/sh

# Write GCP credentials from env var if provided
if [ -n "$GOOGLE_CREDENTIALS_BASE64" ]; then
  echo "$GOOGLE_CREDENTIALS_BASE64" | base64 -d > /app/data/credentials.json
  export GOOGLE_APPLICATION_CREDENTIALS=/app/data/credentials.json
fi

uvicorn fmedia.main:app --host 0.0.0.0 --port $PORT

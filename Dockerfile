# Stage 1: Build dependencies
FROM python:3.11-slim AS build-stage
WORKDIR /app
COPY requirements.txt .
# Install to /root/.local
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final Runtime Image
FROM python:3.11-slim
WORKDIR /app

# Copy from the specific alias 'build-stage'
COPY --from=build-stage /root/.local /root/.local
COPY . .

# Ensure the local bin is in path
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
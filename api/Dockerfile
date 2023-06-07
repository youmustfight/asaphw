FROM python:3.11.3-slim
WORKDIR /usr/src/api

# Install python packages for app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy src
COPY . .

# Env
# --- Secrets
ARG AWS_REGION
ENV AWS_REGION=$AWS_REGION
ARG AWS_ACCESS_KEY_ID
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ARG TARGET_ENV
ENV TARGET_ENV=$TARGET_ENV
# --- Configs (pytorch num_threads, logging, etc.)
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/src/api/src

# Start
EXPOSE 3000
CMD ["python", "-u", "src/start.py"]
 
# Start from an official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for pg_isready
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy the dependency file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

# Copy your application code into the container
COPY . .

# Copy the entrypoint script and make it executable
COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh

# Set the entrypoint script to be executed when the container starts
ENTRYPOINT ["./entrypoint.sh"]

# The command to run the app is specified in the docker-compose.yml
# and will be passed to the entrypoint script
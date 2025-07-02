# Start from an official Python base image
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

# Copy your application code into the container
COPY . .

# The command to run the app is specified in the docker-compose.yml
# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install pip and dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the project files into the container
COPY . /app/

# Expose port (default for Django)
EXPOSE 8000

# Start server using Gunicorn in production, but runserver as fallback dev command
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]

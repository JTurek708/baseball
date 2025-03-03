# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose port 8080 (Cloud Run expects the container to listen on this port)
EXPOSE 8080

# Use Gunicorn to run the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]

# Use an official Python runtime as a parent image
FROM python:3.11-slim


# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files to the app directory
COPY .. /app/

# Expose port 8866 to the outside world
EXPOSE 8866

WORKDIR /app/voila

# Start Django application with live reload
CMD ["voila", "--port=8866", "--no-browser", "--Voila.ip=0.0.0.0"]

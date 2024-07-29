# Use the official Python image from the Docker Hub
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project

# Expose the port the app runs on
EXPOSE 8000

# Start the Django application using Django's development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


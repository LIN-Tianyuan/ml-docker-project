# Use the lightweight official Python image as a base
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# First, copy only the dependency files, taking advantage of Docker's layer caching
# (don't have to reinstall them if the dependencies remain unchanged).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining code and model files
COPY app.py .
COPY model.joblib .

# Declare the port that the container listens on
EXPOSE 8000

# Commands executed when the container starts
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

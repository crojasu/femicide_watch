# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .
COPY .env .env

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install python-dotenv
RUN pip install python-dotenv

# Copy the application files into the container
COPY . .

# Copy the data folder into the container
COPY data /app/data

# Expose the port that the FastAPI application listens on
EXPOSE 8000

# Set the credentials file path as a build-time argument
ARG CREDENTIALS_FILE


# Run the FastAPI application
CMD ["uvicorn", "fmedia.main:app", "--host", "0.0.0.0", "--port", "8000"]

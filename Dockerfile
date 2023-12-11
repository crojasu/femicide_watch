# Use an official Python runtime as the parent image for builder stage
FROM python:3.9-slim as builder

# Install NLTK
RUN pip install nltk

# Create a directory for nltk data
RUN mkdir -p /usr/share/nltk_data

# Download NLTK datasets
RUN python -m nltk.downloader -d /usr/share/nltk_data stopwords punkt wordnet

# Start of the main image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the entry script into the container
COPY entrypoint.sh /app/
# Copy the requirements file into the container
COPY requirements.txt .
COPY .env .env

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY . .

# Copy the data folder into the container
COPY data /app/data

# Copy the NLTK data from builder to main image
COPY --from=builder /usr/share/nltk_data /usr/local/share/nltk_data

# Set the NLTK_DATA environment variable to point to the nltk_data directory in the image
ENV NLTK_DATA /usr/local/share/nltk_data

# Expose the port that the FastAPI application listens on
EXPOSE 8000

# Set the credentials file path as a build-time argument (if you have any credential files)
ARG CREDENTIALS_FILE

# Run the FastAPI application
ENTRYPOINT ["/app/entrypoint.sh"]

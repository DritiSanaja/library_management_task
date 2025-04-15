# Use official Python image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy all files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port Flask will run on
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]

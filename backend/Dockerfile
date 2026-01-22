FROM python:3.11-slim

WORKDIR /app


# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start.sh


# Expose port
EXPOSE 8001

# Start the application using startup script
CMD ["./start.sh"]

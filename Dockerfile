FROM python:3.11-slim

# Install application dependencies
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . /app

# Set default workspace environment variable
ENV GH_COPILOT_WORKSPACE=/app

# Expose dashboard and service ports
EXPOSE 5000 5001 5002 5003 5004 5005 5006 8080

CMD ["python", "main.py"]

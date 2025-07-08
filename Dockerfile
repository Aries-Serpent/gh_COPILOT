FROM python:3.11.6-slim

# Create a non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Set permissions for the application directory
WORKDIR /app
COPY requirements.txt requirements.txt
RUN chown -R appuser:appgroup /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . /app
RUN chown -R appuser:appgroup /app

# Set default workspace environment variable
ENV GH_COPILOT_WORKSPACE=/app

# Switch to the non-root user
USER appuser
# Expose ports for various application functionalities
# Port 5000: Main application API
# Port 5001: Secondary service API
# Port 5002: Internal microservice communication
# Port 5003: Monitoring dashboard
# Port 5004: Logging service
# Port 5005: Authentication service
# Port 5006: Reserved for future use
# Port 8080: Web interface
EXPOSE 5000 5001 5002 5003 5004 5005 5006 8080

CMD ["python", "main.py"]

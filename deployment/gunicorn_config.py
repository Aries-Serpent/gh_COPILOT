"""Gunicorn configuration for serving the web GUI and quantum modules."""

# Socket and port that Gunicorn binds to
bind = "0.0.0.0:8000"

# Number of worker processes handling requests
workers = 3

# Seconds to wait before timing out a worker
timeout = 60

# Logging configuration
loglevel = "info"
accesslog = "-"  # Dash sends logs to stdout

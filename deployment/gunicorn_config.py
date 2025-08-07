"""Gunicorn configuration for serving the web GUI and quantum modules."""

bind = "0.0.0.0:8000"
workers = 3
timeout = 60
loglevel = "info"
accesslog = "-"

import os

# Bind to the port Render provides
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Use 2 workers for better reliability on free tier
workers = 2

# Preload app so it's ready before accepting requests
preload_app = True

# Increase timeout for cold starts (OpenCV imports are slow)
timeout = 120

# Access logging
accesslog = "-"

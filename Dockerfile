FROM python:alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set environment variables for logging (optional, but good practice)
ENV LOG_LEVEL=INFO
ENV LOG_FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Define the command to run your Flask application
CMD ["python", "app.py"]

FROM python:3.9-slim

# Install system dependencies for MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables for email
ENV MAIL_SERVER=smtp.gmail.com
ENV MAIL_PORT=587
ENV MAIL_USE_TLS=True
ENV MAIL_USERNAME=festifysoporte@gmail.com
ENV MAIL_PASSWORD="vipw fzjs jxwe txru"
ENV MAIL_DEFAULT_SENDER=festifysoporte@gmail.com


# Expose port
EXPOSE 5000

# Command to run the application
CMD ["python", "-m", "festify.run"]
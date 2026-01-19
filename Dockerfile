FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Ookla Speedtest CLI
RUN curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash && \
    apt-get update && \
    apt-get install -y speedtest && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY speedtest_monitor.py .

# Create a non-root user
RUN useradd -m -u 1000 speedtest && \
    chown -R speedtest:speedtest /app

USER speedtest

# Run the speedtest once to accept license
RUN speedtest --accept-license --accept-gdpr

# Command to run the application
CMD ["python", "speedtest_monitor.py"]
# Start with the Selenium Standalone Chrome image
FROM selenium/standalone-chrome:latest

# Switch to root to install packages
USER root

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip

# Install your Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy your application code
COPY . /app

# Set working directory
WORKDIR /app

# Run your application
CMD ["python", "your_script.py"]

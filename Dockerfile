# Start with the Selenium Standalone Chrome image
FROM selenium/standalone-chrome:latest

# Switch to root to install packages
USER root

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Install your Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy your application code
COPY . /app

# Set working directory
WORKDIR /app

# Make port 5000 available to the world outside this container
EXPOSE 6020

# Timezone
ENV TZ=Europe/Stockholm
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV SE_OFFLINE=false

# Run your application
CMD ["python3", "-u", "main.py"]
#CMD ["/bin/bash"]

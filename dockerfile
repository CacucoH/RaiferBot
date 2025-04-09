FROM python:3.13-slim

# Project initialization
WORKDIR /app
COPY requirements.txt .

# Install dependencies
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
RUN chmod 775 .

# Set time to Moscow
ENV TZ="Europe/Moscow"

# Copy all files to container
COPY . .

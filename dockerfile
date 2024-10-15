FROM python:3.10-slim as base

# Project initialization
WORKDIR /app
COPY requirements.txt .

# Install dependencies
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
RUN chmod 775 .

# Copy all files to container
COPY . .
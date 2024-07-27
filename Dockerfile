# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory
WORKDIR /cecc

# Create database and log directory
RUN mkdir -p data/

# Copy the current directory contents into the container at /cecc
COPY requirements.txt /cecc
COPY credentials.json /cecc
COPY privkey.pem /cecc
COPY fullchain.pem /cecc
COPY app /cecc/app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 443 available to the world outside this container
EXPOSE 443

# Define environment variable
ENV NAME=CECC

# Run app.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "443", "--log-config", "app/log.ini", "--ssl-keyfile", "privkey.pem", "--ssl-certfile", "fullchain.pem"]

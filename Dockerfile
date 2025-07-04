# Use an official Python runtime as a parent image
FROM gqcv-base

# Set the working directory
WORKDIR /gqcv

# Create database and log directory
RUN mkdir -p data/

# Copy the current directory contents into the container at /gqcv
COPY data/credentials.json /gqcv/data/
COPY app /gqcv/app

# Make port 443 available to the world outside this container
EXPOSE 443

# Define environment variable
ENV NAME=CDC

# Run app.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "443", "--log-config", "app/log.ini", "--ssl-keyfile", "data/privkey.pem", "--ssl-certfile", "data/fullchain.pem", "--header", "App:CDC"]

# Use an official Python runtime as a parent image
FROM cecc-base

# Set the working directory
WORKDIR /cecc

# Create database and log directory
RUN mkdir -p data/

# Copy the current directory contents into the container at /cecc
COPY data/credentials.json /cecc/data/
COPY app /cecc/app

# Make port 443 available to the world outside this container
EXPOSE 443

# Define environment variable
ENV NAME=CECC

# Run app.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "443", "--log-config", "app/log.ini", "--ssl-keyfile", "data/privkey.pem", "--ssl-certfile", "data/fullchain.pem"]

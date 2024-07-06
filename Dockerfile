# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory
WORKDIR /cecc

# Copy the current directory contents into the container at /cecc
COPY app /cecc/app
COPY requirements.txt /cecc
COPY credentials.json /cecc
RUN mkdir -p data/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME CECC

# Run app.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--log-config", "app/log.ini"]

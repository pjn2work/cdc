# CDC Application README

## Description

The CDC application is a Python-based project that can be run either in a Docker container or directly on your local machine. This document provides instructions on how to set up and run the application using both methods.

## Prerequisites

- Docker (if running in a container)
- Python 3.12 (if running locally)
- `pip` (Python package installer)

## Setup

### Running with Docker

1. **Create a `data` directory:**

   Ensure you have a `data` directory in the root of your project. This can be done with the following command:
   ```sh
   mkdir -p data/
   ```

2. **Build the Docker image:**

   Navigate to the root of your project directory and build the Docker image:
  
   ```sh
   docker build -t gqcv-base .
   ```

3. **Run the Docker container:**
  
   After building the image, run the container:
  
   ```sh
   docker run --rm -p 5443:443 -v ./data:/gqcv/data --name cdc-container cdc
   ```

### Running Locally
  
1. **Create a virtual environment (optional but recommended):**
  
   It's good practice to run Python applications in a virtual environment to manage dependencies:
  
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. **Install dependencies:**
  
   Ensure all required packages are installed by running:
  
   ```sh
   pip install -r requirements.txt
   ```
  
3. **Run the application:**
  
   Start the application using uvicorn:
  
   ```sh
   uvicorn app.main:app --host 0.0.0.0 --port 5443 --log-config app/log.ini --reload --ssl-keyfile data/privkey.pem --ssl-certfile data/fullchain.pem
   ```

### File Structure
```
.
├── app
│   ├── main.py
│   ├── log.ini
│   └── ...
├── data
│   ├── credentials.json
│   ├── privkey.pem
│   └── fullchain.pem
├── requirements.txt
└── Dockerfile
```

### Environment Variables
  - NAME: Sets the environment variable for the application name.
### Additional Notes
  - The application exposes port 80 by default in the Docker container.
  - When running locally, the application will be available on port 8080 unless otherwise specified.
  - Ensure credentials.json is correctly configured with the necessary credentials for your application to function.

### Logging

The application uses a logging configuration specified in app/log.ini. Adjust the logging settings as needed for your environment.

### Security
- To Disable TCP Timestamps, because of _Strict-Transport-Security Header Not Set_, edit your **/etc/sysctl.conf** file and add: `sysctl -w net.ipv4.tcp_timestamps=0`.
  
  Then execute the following command: `sudo sysctl -p`

### License
This project is licensed under the Apache License - see the LICENSE.md file for details.
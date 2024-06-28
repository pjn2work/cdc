docker build . -t cdc
docker run -p 8000:80 -v ./data:/cdc/data cdc

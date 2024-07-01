if [ -z "$(docker images -q cdc:latest)" ]; then
  echo Creating image
  docker build . -t cdc
fi
docker run --rm -p 8000:80 -v ./data:/cdc/data cdc

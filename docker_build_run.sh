if [ -z "$(docker images -q cecc-base:latest)" ]; then
  echo Creating cecc-base image
  docker-compose build base || docker build -t cecc-base -f Dockerfile.base . || { echo "Failed to create base image"; exit 1; }
fi

if [ -z "$(docker images -q cecc:latest)" ]; then
  echo Creating cecc image
  docker-compose build app || docker build -t cecc . || { echo "Failed to create app image"; exit 1; }
fi

docker-compose run --rm --service-ports app || docker run --rm -p 8443:443 -v ./data:/cecc/data cecc

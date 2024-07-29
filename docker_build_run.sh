if [ -z "$(docker images -q cecc-base:latest)" ]; then
  echo Creating cecc-base image
  docker-compose build base || docker build -t cecc-base -f Dockerfile.base .
fi

if [ -z "$(docker images -q cecc:latest)" ]; then
  echo Creating cecc image
  docker-compose build app || docker build -t cecc .
fi

docker-compose run --rm --service-ports app || docker run --rm -p 8443:443 -v ./data:/cecc/data cecc

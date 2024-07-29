if [ -z "$(docker images -q cecc-base:latest)" ]; then
  echo Creating cecc-base image
  #docker build -t cecc-base -f Dockerfile.base .
  docker-compose build base
fi

if [ -z "$(docker images -q cecc:latest)" ]; then
  echo Creating cecc image
  #docker build -t cecc .
  docker-compose build app
fi

#docker run --rm -p 8443:443 -v ./data:/cecc/data cecc
docker-compose run --rm --service-ports app

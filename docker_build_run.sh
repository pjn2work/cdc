if [ -z "$(docker images -q cecc-base:latest)" ]; then
  echo ">>> Creating cecc-base image"
  docker-compose build base || docker build -t cecc-base -f Dockerfile.base . || { echo "Failed to create base image"; exit 1; }
fi

if [ "$1" == "update" ] && [ -n "$(docker images -q cecc:latest)" ]; then
  echo ">>> Removing cecc image"
  docker rmi cecc || { echo "Failed to remove app image"; exit 1; }
fi

if [ -z "$(docker images -q cecc:latest)" ]; then
  echo ">>> Creating cecc image"
  docker-compose build app || docker build -t cecc . || { echo "Failed to create app image"; exit 1; }
fi

if command -v docker-compose &> /dev/null; then
  docker-compose run --rm --service-ports app
else
  docker run --rm -p 8443:443 -v ./data:/cecc/data cecc
fi

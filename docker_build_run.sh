function has_docker_compose() {
  if command -v docker-compose &> /dev/null; then
    return 0  # is installed
  else
    return 1
  fi
}

if [ -z "$(docker images -q cecc-base:latest)" ]; then
  echo ">>> Creating cecc-base image"
  if has_docker_compose; then
    docker-compose build base || { echo "Failed to create base image"; exit 1; }
  else
    docker build -t cecc-base -f Dockerfile.base . || { echo "Failed to create base image"; exit 1; }
  fi
fi

if [ "$1" == "update" ] && [ -n "$(docker images -q cecc:latest)" ]; then
  echo ">>> Removing cecc image"
  docker rmi cecc || { echo "Failed to remove app image"; exit 1; }
fi

if [ -z "$(docker images -q cecc:latest)" ]; then
  echo ">>> Creating cecc image"
  if has_docker_compose; then
    docker-compose build app || { echo "Failed to create app image"; exit 1; }
  else
    docker build -t cecc . || { echo "Failed to create app image"; exit 1; }
  fi
fi

if has_docker_compose; then
  docker-compose run --rm --service-ports app
else
  docker run --rm -p 8443:443 -v ./data:/cecc/data cecc
fi

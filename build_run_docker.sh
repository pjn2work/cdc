IMG_NAME="cecc"
LPORT=8443

function has_docker_compose() {
  if command -v docker-compose &> /dev/null; then
    return 0  # 0 = is installed
  else
    return 1
  fi
}

function get_running_pid() {
  PID=$(ps -ef | grep "uvicorn app.main" | grep -v grep | awk '{print $2}')
}

if [ -z "$(docker images -q gqcv-base:latest)" ]; then
  echo ">>> Creating gqcv-base image"
  if has_docker_compose; then
    docker-compose build base || { echo "Failed to create base image"; exit 1; }
  else
    docker build -t gqcv-base -f Dockerfile.base . || { echo "Failed to create base image"; exit 1; }
  fi
fi

if [ "$1" == "update" ] && [ -n "$(docker images -q ${IMG_NAME}:latest)" ]; then
  echo ">>> Removing ${IMG_NAME} image"

  get_running_pid
  if [ -z "$PID" ]; then
    echo "    - 'uvicorn app.main' not running."
  else
    sudo kill -9 $PID
    echo "    - 'uvicorn app.main' with PID $PID has been killed."
  fi

  git pull

  docker rm -f ${IMG_NAME} || { echo "Failed to remove container, may not exist.";}
  docker rmi ${IMG_NAME} || { echo "Failed to remove app image"; exit 1; }
fi

if [ -z "$(docker images -q ${IMG_NAME}:latest)" ]; then
  echo ">>> Creating ${IMG_NAME} image"
  if has_docker_compose; then
    docker-compose build app || { echo "Failed to create app image"; exit 1; }
  else
    docker build -t ${IMG_NAME} . || { echo "Failed to create app image"; exit 1; }
  fi
fi

get_running_pid
if [ -z "$PID" ]; then
  if has_docker_compose; then
    docker-compose run --rm --service-ports app
  else
    nohup docker run --rm -p ${LPORT}:443 -v ./data:/gqcv/data ${IMG_NAME} &
  fi
fi

VERSION=$(curl --silent --insecure https://127.0.0.1:${LPORT}/health)
echo $VERSION

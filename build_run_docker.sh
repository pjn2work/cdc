APP_NAME="CDC"
IMG_NAME="${APP_NAME,,}"
CONTAINER_NAME="${IMG_NAME}-container"
APP_PORT=8443

function has_docker_compose() {
  if command -v docker-compose &> /dev/null; then
    return 0  # 0 = is installed
  else
    return 1
  fi
}

function get_running_pid() {
  PID=$(ps -ef | grep "header App:${APP_NAME}" | grep -v grep | awk '{print $2}')
}

function stop() {
    get_running_pid
    if [ -z "$PID" ]; then
      echo "    - 'uvicorn app.main ${APP_NAME}' not running."
    else
      sudo kill -9 $PID
      echo "    - 'uvicorn app.main ${APP_NAME}' with PID $PID has been killed."
    fi
}

if [ "$1" == "stop" ]; then
  stop
else

  # Create base image if not exists
  if [ -z "$(docker images -q gqcv-base:latest)" ]; then
    echo ">>> Creating gqcv-base image"
    if has_docker_compose; then
      docker-compose build base || { echo "Failed to create base image"; exit 1; }
    else
      docker build -t gqcv-base -f Dockerfile.base . || { echo "Failed to create base image"; exit 1; }
    fi
  fi

  # Stop and remove app image, if exists
  if [ "$1" == "update" ] && [ -n "$(docker images -q ${IMG_NAME}:latest)" ]; then
    echo ">>> Removing ${IMG_NAME} image"

    stop

    git pull

    docker rm -f ${IMG_NAME}
    docker rmi ${IMG_NAME} || { echo "Failed to remove app image"; exit 1; }
  fi

  # Create app image
  if [ -z "$(docker images -q ${IMG_NAME}:latest)" ]; then
    echo ">>> Creating ${IMG_NAME} image"
    if has_docker_compose; then
      docker-compose build app || { echo "Failed to create app image"; exit 1; }
    else
      docker build -t ${IMG_NAME} . || { echo "Failed to create app image"; exit 1; }
    fi
  fi

  # Start app, if not running yet
  get_running_pid
  if [ -z "$PID" ]; then
    if has_docker_compose; then
      docker-compose run --rm --service-ports app --name "${CONTAINER_NAME}"
    else
      nohup docker run --rm -p ${APP_PORT}:443 -v ./data:/gqcv/data --name "${CONTAINER_NAME}" "${IMG_NAME}" &
    fi
  fi

  # Show running version
  VERSION=$(curl --silent --insecure https://127.0.0.1:${APP_PORT}/health)
  echo $VERSION on port $APP_PORT

fi
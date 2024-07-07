if [ -z "$(docker images -q cecc:latest)" ]; then
  echo Creating image
  docker build . -t cecc
fi
docker run --rm -p 8000:80 -v ./data:/cecc/data cecc

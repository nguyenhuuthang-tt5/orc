#!/bin/bash
SCRIPT_DIR=$(cd $(dirname "$0"); pwd)
SERVICE_NAME=ocr
PROJECT_DIR=${SCRIPT_DIR}/../..
DOCKER_IMAGE=${SERVICE_NAME}
DOCKER_REPOSITORY=${DOCKER_IMAGE}
EXPOSE_PORT=80
DEPLOY_ENV=production
cd ${PROJECT_DIR}

### Build docker image ###
echo "Build docker image"
cd ${PROJECT_DIR}
docker build ${BUILD_PARAMS} -f ${SCRIPT_DIR}/Dockerfile -t ${DOCKER_REPOSITORY} .

BUILD_RESULT=$?
if [ ${BUILD_RESULT} -eq 0 ]; then
    echo "Done!"
else
    echo "Docker image build fail"
    exit ${BUILD_RESULT}
fi

echo ">>> Shutdown old docker container <<<"
if [ -n "$(docker ps -q -f name=${DOCKER_IMAGE})" ]; then
    docker stop ${DOCKER_IMAGE}
fi
if [ -n "$(docker ps -a -q -f name=${DOCKER_IMAGE})" ]; then
    docker rm ${DOCKER_IMAGE}
fi
echo "-> DONE"
echo "<<< Shutdown old docker container >>>"

echo ">>> Start new docker container <<<"
docker run -d --name ${DOCKER_IMAGE} --restart=always --log-opt max-size=10m --log-opt max-file=10 \
	 --sysctl net.core.somaxconn=4096 \
	 --ulimit nofile=65536:65536 \
	 -p 0.0.0.0:${EXPOSE_PORT}:80 \
	 -v ${TRANSFER_ROOT}:"/data/transfer/" \
	 -v ${STATIC_ROOT}:"/data/static/app/" \
	 -v ${EXPORT_ROOT}:"/data/export/app/" \
	 -v ${LOG_ROOT}:"/var/log/app" \
	 -v ${UPLOAD_ROOT}:"/data/upload/app/" \
	 -v ${ACCESS_LOG_ROOT}:"/data/log/nginx" \
	 -e DEPLOY_ENV=${DEPLOY_ENV} \
	 -e SERVICE_NAME=${SERVICE_NAME} \
	 -e PROCESSES=${PROCESSES} \
	 ${DOCKER_REPOSITORY}
echo "-> DONE"
echo "<<< Start new docker container >>>"

echo ">>> Clean docker images <<<"
docker logout
docker image prune -a -f
echo "-> DONE!"
echo "<<< Clean docker images >>>"

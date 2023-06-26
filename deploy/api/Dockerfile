FROM ubuntu:focal-20210723
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3-pip nginx && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip && pip --version
RUN pip install --no-cache-dir uwsgi uwsgitop
run pip install djangorestframework

COPY backend/__packages .
RUN pip install --no-cache-dir -r __packages && rm __packages

ENV WEB_DIR=/data/www/web
ENV APP_DIR=/data/www/app
RUN mkdir -p ${WEB_DIR}
RUN mkdir -p ${APP_DIR}
WORKDIR ${APP_DIR}

COPY backend ${APP_DIR}
COPY deploy/api/materials/uwsgi.ini ${APP_DIR}
COPY deploy/api/materials/run.sh ${APP_DIR}

COPY deploy/api/materials/nginx.conf /etc/nginx/sites-enabled/default

EXPOSE 80
CMD [ "sh", "./run.sh"]

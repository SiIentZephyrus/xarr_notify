# 基于镜像基础
FROM python:3.9-alpine3.14

# 复制文件到容器中
COPY . /app/xarr_notify/

# 工作目录 /var/app
WORKDIR /app/xarr_notify

RUN /app/xarr_notify/build/install.sh

EXPOSE 8898

CMD /app/xarr_notify/build/run.sh
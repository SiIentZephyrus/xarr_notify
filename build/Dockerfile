# 基于镜像基础
FROM python:3.9.5

# 复制文件到容器中
ADD ./docker/pip.conf /root/.pip/pip.conf
ADD ./docker/sources.list /etc/apt/sources.list
ADD ./docker/openssl.cnf /etc/ssl/openssl.cnf
ADD ./docker/localtime /etc/localtime
ADD ./requirements.txt /var/requirements.txt
ADD ./docker/startup.sh /var/startup.sh
ADD ./config/install.sh /var/install.sh

# 工作目录 /var/app
WORKDIR /var/app

RUN /var/install.sh

CMD /var/startup.sh
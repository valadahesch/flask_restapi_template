# 构建环境镜像
FROM python:3.9.16 as env
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list\
&& apt-get update && apt-get install -y python3-dev libxml2-dev libxslt-dev libvirt-dev zlib1g-dev
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -\
&& curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list\
&& apt-get update\
&& DEBIAN_FRONTEND=noninteractive ACCEPT_EULA=Y apt-get install -y msodbcsql17\
&& DEBIAN_FRONTEND=noninteractive ACCEPT_EULA=Y apt-get install -y mssql-tools\
&& echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc\
&& /bin/bash -c "source ~/.bashrc"\
&& apt-get install -y unixodbc-dev
RUN apt-get install -y redis-server
# 构建依赖镜像
FROM python/techadmin_env:latest as requirement
ADD requirements.txt /requirements.txt
RUN export pypiDomain=mirrors.aliyun.com \
&& pip config set global.index-url http://$pypiDomain/pypi/simple/\
&& pip config set global.trusted-host $pypiDomain\
&& pip install -U pip\
&& pip install --upgrade pip setuptools\
&& pip install --user -r requirements.txt
# 构建程序镜像
FROM python/techadmin:latest as project
# 设置代码文件夹工作目录 /app
WORKDIR /techadmin
# 复制当前代码文件到容器中 /app
ADD . /techadmin/
# 设置系统时区
ENV TZ="Asia/Shanghai"
# 添加执行文件可执行权限
RUN chmod +x run.sh
# 暴露的端口号
EXPOSE 8000
# Run app.py when the container launches
CMD /techadmin/run.sh
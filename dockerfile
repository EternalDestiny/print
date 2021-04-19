FROM python:3.8
RUN mkdir -p /chen
WORKDIR /chen
COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt /chen/
RUN pip install -r /chen/requirements.txt
RUN rm -rf /chen
COPY . /chen
CMD ["python","./manage.py","runserver","0.0.0.0:8000"]



#  FROM python:3.8.3  # 创建目录
#  mkdir -p /usr/src/app  # 设置工作目录
#  WORKDIR /usr/src/app    # 将pip.conf文件复制到/root/.pip/pip.conf
#  COPY pip.conf /root/.pip/pip.conf  # 更新pip
#  RUN pip install --upgrade pip  # 下载django和uwsgi 在一般项目中只需下载requirement.txt
#  RUN pip install django && pip install uwsgi  # 将当前目录下的文件全部复制过去，只有是复制项目，uwsgi配置文件
#  COPY . /usr/src/app/  # 在run的时候启动uwsgi
#  CMD uwsgi --ini uwsgi_conf.ini  # 暴露端口
#  EXPOSE 80 8080 8000 8888
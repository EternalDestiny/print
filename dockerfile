FROM python:3.8
RUN mkdir -p /chen
WORKDIR /chen
#更改pip配置，使用国内镜像源
COPY pip.conf /root/.pip/pip.conf
#安装项目依赖的python包
COPY requirements.txt /chen/
RUN pip install -r /chen/requirements.txt
RUN rm -rf /chen
COPY . /chen
CMD ["python","./manage.py","runserver","0.0.0.0:8000"]
FROM python:3.8
RUN mkdir -p /chen
WORKDIR /chen
#COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt /chen/
RUN pip install -r /chen/requirements.txt
RUN rm -rf /chen
COPY . /chen
CMD ["python","./manage.py","runserver","0.0.0.0:8000"]
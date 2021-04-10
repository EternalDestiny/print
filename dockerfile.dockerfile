FROM python:3.8
RUN mkdir -p /home/chen/app
WORKDIR /home/chen/app
COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt /home/chen/app/
RUN pip install -r /home/chen/app/requirements.txt
RUN rm -rf /home/chen/app
COPY . /home/chen/app
CMD ["python","./manage.py","runserver","0.0.0.0:8000"]
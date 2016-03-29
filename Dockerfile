FROM python:2.7.10-wheezy
MAINTAINER Zheng Guang "zg.zhu@daocloud.io"

WORKDIR /code

RUN echo "Asia/Shanghai" > /etc/timezone && \
        dpkg-reconfigure -f noninteractive tzdata
RUN apt-get update && apt-get -qqy install python-pip

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD . /code

EXPOSE 5000

# Start python
CMD ["python2", "dao_auto_scale.py"]

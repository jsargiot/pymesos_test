FROM python:2.7-alpine

WORKDIR /app

ENTRYPOINT ["python"]

CMD ["/app/framework.py"]

RUN pip install kazoo==2.0 protobuf==3.5.2 mesos.interface==1.7.1 pymesos==0.1.7

ADD framework.py /app

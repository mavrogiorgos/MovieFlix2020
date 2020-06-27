FROM ubuntu:16.04 
RUN apt-get update
RUN apt-get install -y python3 python3-pip 
RUN pip3 install flask pymongo wtforms
RUN mkdir /app
RUN mkdir -p /app/data
COPY myapp.py /app/myapp.py 
COPY templates /app/templates 
COPY static /app/static  
ADD data /app/data 
EXPOSE 5000
WORKDIR /app
ENTRYPOINT [ "python3","-u", "myapp.py" ]


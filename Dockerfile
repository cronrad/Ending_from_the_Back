FROM python:3.8
ENV HOME /root
WORKDIR /root
COPY . .
# Download dependancies
RUN pip3 install bcrypt
RUN pip3 install pymongo
RUN pip3 install flask


EXPOSE 8080
EXPOSE 27017

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD python3 -u server.py
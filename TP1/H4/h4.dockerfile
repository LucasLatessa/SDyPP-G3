FROM python:3.13.0a5-alpine3.19

RUN mkdir -p /usr/local/src/H4

ADD H4/Serv_Cli.py /usr/local/src/H4/Serv_Cli.py

EXPOSE 8080
WORKDIR /usr/local/src/H4
CMD ["python3", "Serv_Cli.py" ]     
#ENTRYPOINT ["/bin/sleep", "10"] 
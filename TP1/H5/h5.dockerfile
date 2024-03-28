FROM python:3.13.0a5-alpine3.19

RUN mkdir -p /usr/local/src/H5

ADD H5/Serv_Cli.py /usr/local/src/H5/Serv_Cli.py
EXPOSE 8080

WORKDIR /usr/local/src/H5

# Definir el comando principal utilizando ENTRYPOINT
ENTRYPOINT ["python3", "Serv_Cli.py"]

# Proporcionar argumentos predeterminados utilizando CMD
CMD [HOSTServ,PORTServ,HOSTDest,PORTDest]
#ENTRYPOINT ["/bin/sleep", "10"] 


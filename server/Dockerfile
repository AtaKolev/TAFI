FROM python:3.8

ENV TZ=Europe/Sofia
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR    /opt/oracle

RUN        apt-get update && apt-get install -y libaio1 wget unzip \
            && wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basic-linuxx64.zip \
            && unzip instantclient-basic-linuxx64.zip \
            && rm -f instantclient-basic-linuxx64.zip \
            && cd /opt/oracle/instantclient* \
            && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci \
            && echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf \
            && ldconfig

WORKDIR    /app

COPY app/* ./
RUN apt-get update \
&& pip3 install --upgrade pip \
&& apt-get update \
&& apt-get update \
&& ACCEPT_EULA=Y apt-get -y install --no-install-recommends unixodbc\
    unixodbc-dev\
    freetds-dev \
    freetds-bin\
	tdsodbc\
&& apt-get install --reinstall build-essential -y \ 
&& apt-get clean

RUN pip3 install -r requirements.txt

EXPOSE 3500
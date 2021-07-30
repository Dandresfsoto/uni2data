FROM ubuntu:18.04

ENV PYTHONUNBUFFERED 1

# Set the locale
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen es_CO.UTF-8
ENV LANG='es_CO.UTF-8' LANGUAGE='es_CO:es_ES:es' LC_ALL='es_CO.UTF-8'
RUN echo es_CO.UTF-8 UTF-8 >> /etc/locale.gen && locale-gen

# apt-get and system utilities
RUN apt-get update && apt-get install -y \
    curl apt-utils apt-transport-https debconf-utils gcc build-essential python-dev python3-dev libssl-dev libxrender-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev wget python-pip g++-5\
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends xvfb libfontconfig libjpeg-turbo8 xfonts-75dpi fontconfig

RUN wget --no-check-certificate https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb
RUN chmod 777 wkhtmltox_0.12.5-1.bionic_amd64.deb
RUN apt install ./wkhtmltox_0.12.5-1.bionic_amd64.deb -y
RUN rm wkhtmltox_0.12.5-1.bionic_amd64.deb

# adding custom MS repository
#RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

#RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# install SQL Server drivers
#RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

# install SQL Server tools
#RUN apt-get update && ACCEPT_EULA=Y apt-get install -y mssql-tools
#RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
#RUN /bin/bash -c "source ~/.bashrc"



# python libraries
RUN apt-get update && apt-get install -y \
    python3-pip python3-dev python3-setuptools \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*


# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip3 install --no-cache-dir -r /requirements/prod.txt \
    && rm -rf /requirements

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint
#RUN chown django /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start
#RUN chown django /start


COPY ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r//' /start-celeryworker
RUN chmod +x /start-celeryworker
#RUN chown django /start-celeryworker


COPY ./compose/production/django/celery/flower/start /start-flower
RUN sed -i 's/\r//' /start-flower
RUN chmod +x /start-flower


COPY ./compose/production/django/daphne/start /start-daphne
RUN sed -i 's/\r//' /start-daphne
RUN chmod +x /start-daphne


COPY . /app

RUN rm -rf /app/styles/
RUN rm -rf /app/.envs/
RUN rm -rf /app/.venv/
RUN rm -rf /app/.vscode

#RUN chown -R django /app

#USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
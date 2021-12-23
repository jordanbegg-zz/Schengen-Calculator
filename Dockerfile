FROM python:3.9-buster

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && apt-get upgrade -y
RUN ACCEPT_EULA=Y apt-get install -y unixodbc unixodbc-dev msodbcsql17

RUN useradd schengen_calculator

WORKDIR /home/schengen_calculator

# Poetry set up
RUN python3 -m pip install --upgrade pip
RUN pip3 install poetry
RUN poetry config virtualenvs.create false

# Install Python dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry add gunicorn pymysql cryptography
RUN poetry install

COPY app app
COPY migrations migrations
COPY schengen_calculator.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP schengen_calculator.py

RUN chown -R schengen_calculator:schengen_calculator ./
USER schengen_calculator

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
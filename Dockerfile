FROM python:3.9.0b5-alpine3.12
COPY . /app
WORKDIR /app
RUN apk add bash
RUN python -m pip install --upgrade pip
RUN pip install -r python-dependencies.txt

EXPOSE 5000/tcp
RUN chmod +x startup.sh

CMD ["bash", "startup.sh"]
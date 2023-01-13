FROM python:3.7-alpine
WORKDIR /workspace

COPY 1_data_proxy/requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8082 5683/udp
COPY settings.json settings.json
COPY 1_data_proxy .

CMD ["python3", "-m", "server"]

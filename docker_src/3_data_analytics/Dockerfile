FROM python:3.9
WORKDIR /workspace

COPY 3_data_analytics/requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY settings.json settings.json
COPY 3_data_analytics .

CMD ["python3", "-m", "data_predictions"]

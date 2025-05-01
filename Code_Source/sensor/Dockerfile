FROM python:3.9-slim

RUN pip install kafka-python retrying
COPY sensors_mock.py .

CMD ["python", "sensors_mock.py"]
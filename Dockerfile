FROM python:3.11

ADD reader.py .

RUN pip install --no-cache-dir flask matplotlib requests

EXPOSE 5000

CMD ["python", "reader.py"]

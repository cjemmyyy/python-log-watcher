FROM python:3.9-slim

WORKDIR /app

RUN pip install requests

COPY watcher.py .

ENV PYTHONUNBUFFERED=1

RUN python -m py_compile watcher.py

CMD ["python", "watcher.py"]

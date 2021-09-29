FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Working Area
WORKDIR /app
COPY ./app /app

# python package install
RUN pip install -r /app/requirements.txt

ENV DOCKER_CONTAINER=1

EXPOSE 5000

CMD ["export", "PYTHONPATH=/app"]
CMD ["uvicorn", "app:cathay_api", "--host", "0.0.0.0", "--port", "5000"]

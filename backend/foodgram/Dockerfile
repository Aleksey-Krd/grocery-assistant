FROM python:3.9-slim
WORKDIR /code
COPY . .
RUN pip install -U pip &&\
    pip install -r requirements.txt --no-cache-dir
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
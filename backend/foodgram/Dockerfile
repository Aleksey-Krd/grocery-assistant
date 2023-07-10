FROM python:3.9-slim
WORKDIR /code
COPY . .
WORKDIR /code/foodgram
RUN pip install -U pip &&\
    pip install -r requirements.txt --no-cache-dir
RUN chmod +x run_app.sh
ENTRYPOINT [ "sh", "/code/foodgram/run_app.sh" ]
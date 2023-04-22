FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY ./requirements.txt /app/requirements.txt

# RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./app /app

# docker build -t my_books_image:latest .
# docker run -d --name my_books -p 8000:8000 my_books_image:latest

# docker run -d --name my_books_redis -v ${PWD}/local_data_redis:/data -p 10001:6379 -p 13333:8001 redis/redis-stack:latest
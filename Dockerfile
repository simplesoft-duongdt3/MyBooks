FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY ./requirements.txt /app/requirements.txt

# RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./app /app

# docker build -t my_books_image:latest .
# docker run -d --name my_books -p 8000:8000 my_books_image:latest
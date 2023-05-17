# python3.10 -m virtualenv venv
source venv/bin/activate

# python -m pip install -r requirements.txt

cd app
python api.py
# gunicorn api:app --access-logfile `pwd`/logs/gunicorn_access.log --error-logfile `pwd`/logs/gunicorn_error.log --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000  --daemon

# Stop
# kill -9 `ps aux | grep gunicorn | grep api:app | awk '{ print $2 }'`

# docker run -d --name redis-stack-vector-books -v `pwd`/data-vector-redis/:/data -p 10001:6379 -p 13333:8001 redis/redis-stack:latest
# redis UI port 13333
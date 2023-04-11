source venv/bin/activate

cd app
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000  --daemon

# Stop
# kill -9 `ps aux | grep gunicorn | grep api:app | awk '{ print $2 }'`
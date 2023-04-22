# python3.10 -m virtualenv venv
source venv/bin/activate

# python -m pip install -r requirements.txt

cd app
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000  --daemon

# Stop
# kill -9 `ps aux | grep gunicorn | grep api:app | awk '{ print $2 }'`
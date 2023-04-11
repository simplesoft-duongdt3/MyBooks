# MyBooks
 
docker run --detach     --name tinyflutterteam_landing_page     --restart=always     --env "VIRTUAL_HOST=tinyflutterteam.com"     --env "VIRTUAL_PORT=80"     --env "LETSENCRYPT_HOST=tinyflutterteam.com"     --env "LETSENCRYPT_EMAIL=doanthanhduong11031990@gmail.com"     tinyflutterteam.com:latest

docker run --detach --name nocodb --restart=always --env "VIRTUAL_HOST=tinyflutterteam.com"     --env "VIRTUAL_PORT=8080" --env "VIRTUAL_PATH=/books"     --env "LETSENCRYPT_HOST=tinyflutterteam.com"     --env "LETSENCRYPT_EMAIL=doanthanhduong11031990@gmail.com" -v "$(pwd)"/nocodb:/usr/app/data/ -p 8080:8080 nocodb/nocodb:latest

docker run --detach --name nocodb --restart=always --env "VIRTUAL_HOST=tinyflutterteam.com"     --env "VIRTUAL_PORT=8080"      --env "LETSENCRYPT_HOST=tinyflutterteam.com"     --env "LETSENCRYPT_EMAIL=doanthanhduong11031990@gmail.com" -v "$(pwd)"/nocodb:/usr/app/data/ --expose 8080 nocodb/nocodb:latest


docker exec dba7cece9b4c nginx -T

docker run --detach --name nocodb --restart=always --env "VIRTUAL_HOST=tinyflutterteam.com"     --env "VIRTUAL_PORT=8080"      --env "LETSENCRYPT_HOST=tinyflutterteam.com"     --env "LETSENCRYPT_EMAIL=doanthanhduong11031990@gmail.com" -v "$(pwd)"/nocodb:/usr/app/data/ --expose 8080 nocodb/nocodb:latest
docker run --detach -e TZ=Asia/Bangkok --name nocodb --restart=always  -p 8080:8080 -v "$(pwd)"/nocodb:/usr/app/data/ nocodb/nocodb:latest


docker run -d --name nocodb -v "$(pwd)"/nocodb:/usr/app/data/ --volume /etc/timezone:/etc/timezone:ro --volume /etc/localtime:/etc/localtime:ro -p 8080:8080 nocodb/nocodb:latest

http://103.221.220.249:8080/

Books

Name
Status (Draft, Active, Deleted)
Authors
Published Year
Published By
ThumbImage

BookCollections
Name
BooksInCollection

Books_BookCollections_MM





docker run --detach     --name nginx-proxy     --restart=always     --publish 80:80     --publish 443:443     --volume certs:/etc/nginx/certs     --volume vhost:/etc/nginx/vhost.d     --volume html:/usr/share/nginx/html     --volume /var/run/docker.sock:/tmp/docker.sock:ro     nginxproxy/nginx-proxy:latest

docker run --detach     --name nginx-proxy-acme     --restart=always     --volumes-from nginx-proxy     --volume /var/run/docker.sock:/var/run/docker.sock:ro     --volume acme:/etc/acme.sh     --env "DEFAULT_EMAIL=doanthanhduong11031990@gmail.com"     nginxproxy/acme-companion:latest

docker run --detach     --name tinyflutterteam_landing_page     --restart=always     --env "VIRTUAL_HOST=tinyflutterteam.com"     --env "VIRTUAL_PORT=80"     --env "LETSENCRYPT_HOST=tinyflutterteam.com"     --env "LETSENCRYPT_EMAIL=doanthanhduong11031990@gmail.com"     tinyflutterteam.com:latest


docker run -d --name nocodb --volume /etc/timezone:/etc/timezone:ro --volume /etc/localtime:/etc/localtime:ro -p 8080:8080 nocodb/nocodb:latest


Name

python -m pip freeze > requirements.txt
# Update all package
pip install -U -r requirements.txt

# Update a package
pip install -U fastapi

# check broken package
python -m pip check

python -m pip install -r requirements.txt


How to Create Python Requirements File After Development
pip install pipreqs

running pipreqs in the command line generates a requirements.txt file automatically:
$ pipreqs /home/project/location
Successfully saved requirements file in   /home/project/location/requirements.txt

python3.10 -m pip install virtualenv

python3.10 -m virtualenv venv

source venv/bin/activate




python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
python -m pip install img2vec_pytorch
python -m pip install Pillow
python -m pip install scikit-learn
python -m pip install fastapi
python -m pip install uvicorn
python -m pip install python-multipart
python -m pip install pydantic
python -m pip install requests
python -m pip install loguru
python -m pip install gunicorn
python -m pip install python-dotenv

cd app
uvicorn api:app --reload

gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000  --daemon

kill -9 `ps aux | grep gunicorn | grep api:app | awk '{ print $2 }'`

ps ax|grep gunicorn

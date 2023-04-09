# MyBooks
 
docker run --detach     --name tinyflutterteam_landing_page     --restart=always     --env "VIRTUAL_HOST=tinyflutterteam.com"     --env "VIRTUAL_PORT=80"     --env "LETSENCRYPT_HOST=tinyflutterteam.com"     --env "LETSENCRYPT_EMAIL=doanthanhduong11031990@gmail.com"     tinyflutterteam.com:latest

docker run --detach --name nocodb --restart=always --env "VIRTUAL_HOST=tinyflutterteam.com"     --env "VIRTUAL_PORT=8080" --env "VIRTUAL_PATH=/books"     --env "LETSENCRYPT_HOST=tinyflutterteam.com"     --env "LETSENCRYPT_EMAIL=doanthanhduong11031990@gmail.com" -v "$(pwd)"/nocodb:/usr/app/data/ -p 8080:8080 nocodb/nocodb:latest

docker run --detach --name nocodb --restart=always --env "VIRTUAL_HOST=tinyflutterteam.com"     --env "VIRTUAL_PORT=8080"      --env "LETSENCRYPT_HOST=tinyflutterteam.com"     --env "LETSENCRYPT_EMAIL=doanthanhduong11031990@gmail.com" -v "$(pwd)"/nocodb:/usr/app/data/ --expose 8080 nocodb/nocodb:latest


docker exec dba7cece9b4c nginx -T

docker run --detach --name nocodb --restart=always --env "VIRTUAL_HOST=tinyflutterteam.com"     --env "VIRTUAL_PORT=8080"      --env "LETSENCRYPT_HOST=tinyflutterteam.com"     --env "LETSENCRYPT_EMAIL=doanthanhduong11031990@gmail.com" -v "$(pwd)"/nocodb:/usr/app/data/ --expose 8080 nocodb/nocodb:latest
docker run --detach -e TZ=Asia/Bangkok --name nocodb --restart=always  -p 8080:8080 -v "$(pwd)"/nocodb:/usr/app/data/ nocodb/nocodb:latest


docker run -d --name nocodb -v "$(pwd)"/nocodb:/usr/app/data/ --volume /etc/timezone:/etc/timezone:ro --volume /etc/localtime:/etc/localtime:ro -p 8080:8080 nocodb/nocodb:latest

http://103.221.220.249:8080/



docker run --detach     --name nginx-proxy     --restart=always     --publish 80:80     --publish 443:443     --volume certs:/etc/nginx/certs     --volume vhost:/etc/nginx/vhost.d     --volume html:/usr/share/nginx/html     --volume /var/run/docker.sock:/tmp/docker.sock:ro     nginxproxy/nginx-proxy:latest

docker run --detach     --name nginx-proxy-acme     --restart=always     --volumes-from nginx-proxy     --volume /var/run/docker.sock:/var/run/docker.sock:ro     --volume acme:/etc/acme.sh     --env "DEFAULT_EMAIL=doanthanhduong11031990@gmail.com"     nginxproxy/acme-companion:latest

docker run --detach     --name tinyflutterteam_landing_page     --restart=always     --env "VIRTUAL_HOST=tinyflutterteam.com"     --env "VIRTUAL_PORT=80"     --env "LETSENCRYPT_HOST=tinyflutterteam.com"     --env "LETSENCRYPT_EMAIL=doanthanhduong11031990@gmail.com"     tinyflutterteam.com:latest


docker run -d --name nocodb --volume /etc/timezone:/etc/timezone:ro --volume /etc/localtime:/etc/localtime:ro -p 8080:8080 nocodb/nocodb:latest


python3.10 -m pip install virtualenv

python3.10 -m virtualenv venv
source venv/bin/activate

python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
python -m pip install img2vec_pytorch
python -m pip install Pillow
python -m pip install scikit-learn
python -m pip install fastapi



from fastapi import FastAPI
import time
import pickle
import codecs
from img2vec_pytorch import Img2Vec
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Initialize Img2Vec with GPU
img2vec = Img2Vec(cuda=False)

@app.get("/")
async def root():
    time_start = time.time()

    # Read in an image (rgb format)
    img = Image.open('test.jpg')
    # Get a vector from img2vec, returned as a torch FloatTensor
    vec = img2vec.get_vec(img, tensor=True)
    #print(vec)
    pickled = pickle.dumps(vec)

    print(f"length of {len(pickled)}")

    base64Data = codecs.encode(pickled, "base64").decode()

    print(base64Data)

    decodeData = pickle.loads(codecs.decode(base64Data.encode(),'base64'))

    print(f"length of {len(decodeData)}")
    #print(decodeData)

    distance = cosine_similarity(vec.reshape((1, -1)), decodeData.reshape((1, -1)))[0][0]


    time_end = time.time()

    print("distance = " + str(distance) + " time= " + str(time_end - time_start))

    return {"message": "Hello World"}
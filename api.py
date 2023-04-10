from typing import Annotated
import base64
import json
from fastapi import FastAPI, File, UploadFile
import requests

import time
from datetime import datetime
import pickle
import codecs
from img2vec.img2vec_pytorch.img_to_vec import Img2Vec
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Initialize Img2Vec with GPU
img2vec = Img2Vec(cuda=False, model='resnet18')

@app.get("/")
async def root():
    time_start = time.time()

    # Read in an image (rgb format)
    img = Image.open('b01.jpg')
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

    img2 = Image.open('b02.jpg')
    vec2 = img2vec.get_vec(img2, tensor=True)

    distance2 = cosine_similarity(vec.reshape((1, -1)), vec2.reshape((1, -1)))[0][0]
    time_end = time.time()
    print("distance2 = " + str(distance2) + " time= " + str(time_end - time_start))
    

    img3 = Image.open('b01_1.jpg')
    vec3 = img2vec.get_vec(img3, tensor=True)

    distance3 = cosine_similarity(vec.reshape((1, -1)), vec3.reshape((1, -1)))[0][0]
    time_end = time.time()
    print("distance3 = " + str(distance3) + " time= " + str(time_end - time_start))
    

    return {"message": "Hello World"}


# http://103.221.220.249:8080/api/v1/db/storage/upload?path=noco%2FMyBooks%2FBooks%2FThumbImage
# [
#   {
#     "path": "download/noco/MyBooks/Books/ThumbImage/ZiP19ye8lom1Ey_Uva.jpg",
#     "title": "b03.jpg",
#     "mimetype": "image/jpeg",
#     "size": 169120
#   }
# ]


# http://103.221.220.249:8080/api/v1/db/meta/audits/rows/4/update
# {"fk_model_id":"md_mzf11ykged3ibq","column_name":"ThumbImage","row_id":"4","value":"[{\"path\":\"download/noco/MyBooks/Books/ThumbImage/ZiP19ye8lom1Ey_Uva.jpg\",\"title\":\"b03.jpg\",\"mimetype\":\"image/jpeg\",\"size\":169120}]","prev_value":"[object Object]"}
def create_book(result_upload):
    try:
        print(f'create_book {result_upload}')
        url = "http://103.221.220.249:8080/api/v1/db/data/v1/MyBooks/Books"

        payload = json.dumps({
            # "Name": "b1",
            # "Authors": "Nuyen Minh Hoa",
            # "Published Year": "2019",
            # "Published By": "NXB Tong hop",
            "ThumbImage": result_upload
        })
        headers = {
            'accept': 'application/json',
            'xc-token': '5Bdhl77iJJ1fIbF2fPb8hcCceNzSJvmt4NIya0aR',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return json.loads(response.text)
    except Exception:
        return None

@app.post("/upload")
async def create_file(
    file: Annotated[UploadFile, File()],
):
    try:
        contents = file.file.read()
        # base64_bytes = base64.b64encode(contents)
        # base64_message = base64_bytes.decode('utf8')
        today = datetime.now()
        str_date_time = today.strftime("%Y%m%d-%H%M%S%f") + "-" + str(file.filename)

        url = "http://103.221.220.249:8080/api/v1/db/storage/upload?path=MyBooks/Books/attachment/20230410"

        payload={}
        files=[
            ('file',(str(file.filename),contents,str(file.content_type)))
        ]
        headers = {
            'xc-token': '5Bdhl77iJJ1fIbF2fPb8hcCceNzSJvmt4NIya0aR'
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        response_list = json.loads(response.text) 
        print(str(response_list))
        if response_list:
            result_create_book = create_book(response_list)
        return {
            "date_time": str_date_time,
            "file_name": file.filename,
            "file_size": file.size,
            # "file": base64_message,
            "file_content_type": file.content_type,
            "result_create_book": result_create_book
        }
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
    
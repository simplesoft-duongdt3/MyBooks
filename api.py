from typing import Annotated
import base64
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
import requests
import io
import time
from datetime import datetime
import pickle
import codecs
# from img2vec.img2vec_pytorch.img_to_vec import Img2Vec
from img2vec_pytorch import Img2Vec
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import logging
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

app = FastAPI()
api_endpoint = "http://103.221.220.249:8080"
# Initialize Img2Vec with GPU
img2vec = Img2Vec(cuda=False, model='resnet18')


def check_feature_vector_all_exists_books(image_feature_vector):
    list_book_similar = []
    
    time_start = time.time()
    url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/Books?fields=Id%2CName%2CThumbImage%2CThumb%20Image%20Feature%20Vector&where=where%3D%28Status%2Ceq%2CActive%29&limit=100&offset=0"

    payload={}
    headers = {
        'accept': 'application/json',
        'xc-token': '5Bdhl77iJJ1fIbF2fPb8hcCceNzSJvmt4NIya0aR'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    result = json.loads(response.text)
    if result:
        list_book = result['list']
        for book in list_book:
            book_feature_vector = book['Thumb Image Feature Vector']
            book_id = book['Id']
            thumb_image_list = book['ThumbImage']
            thumb_image = None
            if thumb_image_list:
                thumb_image = thumb_image_list[0]
            book_name = book['Name']
            if book_feature_vector:
                decodeData = pickle.loads(codecs.decode(book_feature_vector.encode(),'base64'))

                distance = cosine_similarity(image_feature_vector.reshape((1, -1)), decodeData.reshape((1, -1)))[0][0]
                if distance >= 0.9:
                    list_book_similar.append({
                        'id': book_id,
                        'name': book_name,
                        'thumb_image': thumb_image,
                        'distance': str(distance)
                    })
                print("Id = " + str(book_id) + " distance = " + str(distance))
    time_end = time.time()
    print("check_feature_vector_all_exists_books time= " + str(time_end - time_start))
    return list_book_similar

def get_image_feature_vector(file_content):
    # Read in an image (rgb format)
    img = Image.open(io.BytesIO(file_content))
    # Get a vector from img2vec, returned as a torch FloatTensor
    vec = img2vec.get_vec(img, tensor=True)
    return vec

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

def create_draft_book(result_upload, feature_vector_base64):
    try:
        print(f'create_draft_book {result_upload}')
        url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/DraftBooks"

        payload = json.dumps({
            "ThumbImage": result_upload,
            "Thumb Image Feature Vector": feature_vector_base64
        })
        headers = {
            'accept': 'application/json',
            'xc-token': '5Bdhl77iJJ1fIbF2fPb8hcCceNzSJvmt4NIya0aR',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return json.loads(response.text)
    except Exception:
        logging.exception("create_draft_book: An exception was thrown!")
        return None

def create_book(thumbImage, feature_vector_base64, name, author, published_year, published_by):
    try:
        time_start = time.time()
        logging.info(f'create_book {str(name)} {str(thumbImage)}')
        url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/Books"

        payload = json.dumps({
            "Name": name,
            "Authors": author,
            "Published Year": str(published_year),
            "Published By": published_by,
            "ThumbImage": thumbImage,
            "Thumb Image Feature Vector": feature_vector_base64
        })
        headers = {
            'accept': 'application/json',
            'xc-token': '5Bdhl77iJJ1fIbF2fPb8hcCceNzSJvmt4NIya0aR',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        logging.info(f'create_book response {str(response)}')
        time_end = time.time()
        logging.info("create_book time= " + str(time_end - time_start))
        return json.loads(response.text)
    except Exception:
        logging.exception("create_book: An exception was thrown!")
        return None

def encode_base64_feature_vector(feature_vector):
    pickled = pickle.dumps(feature_vector)
    base64Data = codecs.encode(pickled, "base64").decode()
    return base64Data

def upload_file_image(file_name, file_contents, content_type):
    try:
        time_start = time.time()
        logging.info(f"upload_file_image: file_name {file_name} content_type {content_type}")
        today = datetime.now()
        str_date_time = today.strftime("%Y%m%d")

        url = f"{api_endpoint}/api/v1/db/storage/upload?path=MyBooks/Books/attachment/{str_date_time}"

        payload={}
        files=[
            ('file',(str(file_name), file_contents, str(content_type)))
        ]
        headers = {
            'xc-token': '5Bdhl77iJJ1fIbF2fPb8hcCceNzSJvmt4NIya0aR'
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        response_list = json.loads(response.text)
        logging.info(f"upload_file_image response {str(response_list)}")

        time_end = time.time()
        logging.info("upload_draft_image time= " + str(time_end - time_start))
        return response_list
    except Exception as e:
        logging.exception("upload_file_image: An exception was thrown!")
        return None

@app.post("/upload")
async def upload_draft_image(
    file: Annotated[UploadFile, File()],
):
    try:
        time_start = time.time()
        contents = file.file.read()

        feature_vector = get_image_feature_vector(contents)
        feature_vector_base64 = encode_base64_feature_vector(feature_vector)
        list_book_similar = check_feature_vector_all_exists_books(feature_vector)

        # base64_bytes = base64.b64encode(contents)
        # base64_message = base64_bytes.decode('utf8')
        response_list = upload_file_image(file.filename, contents, file.content_type)

        if response_list:
            result_create_draft_book = create_draft_book(response_list, feature_vector_base64)

        time_end = time.time()
        logging.info("upload_draft_image time= " + str(time_end - time_start))    
        return {
            # "file_name": file.filename,
            # "file_size": file.size,
            # "file": base64_message,
            # "file_content_type": file.content_type,
            "result_create_draft_book": result_create_draft_book,
            'list_book_similar': list_book_similar
        }
    except Exception as e:
        logging.exception("upload_draft_image: An exception was thrown!")
        raise HTTPException(status_code=500, detail="Error: " + str(e))
    finally:
        file.file.close()
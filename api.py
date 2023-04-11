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
from request_models import BookRequestToDb, CreateNewBookRequest
from response_models import Book, BookListResponse, BookListResponseFromDb, BookSimilarItem, CreateDraftBookResponse, DraftBook, DraftBookListResponse, ListBookSimilarResponse

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import logging
logging.basicConfig()
logger = logging.getLogger('app_log')
logger.setLevel(logging.INFO)

app = FastAPI()
api_endpoint = "http://103.221.220.249:8080"
# Initialize Img2Vec with GPU
img2vec = Img2Vec(cuda=False, model='resnet18')

def check_feature_vector_all_exists_books(image_feature_vector) -> ListBookSimilarResponse:
    list_book_similar: list[BookSimilarItem] = []
    
    time_start = time.time()
    url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/Books?fields=Id%2CName%2CThumbImage%2CThumb%20Image%20Feature%20Vector&where=where%3D%28Status%2Ceq%2CActive%29&limit=100&offset=0"

    payload={}
    headers = {
        'accept': 'application/json',
        'xc-token': '5Bdhl77iJJ1fIbF2fPb8hcCceNzSJvmt4NIya0aR'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    bookListDb: BookListResponseFromDb = BookListResponseFromDb.parse_raw(response.text)
    if bookListDb and bookListDb.list:
        for book in bookListDb.list:
            book_feature_vector = book.Thumb_Image_Feature_Vector
            if book_feature_vector:
                decodeData = pickle.loads(codecs.decode(book_feature_vector.encode(),'base64'))

                distance = cosine_similarity(image_feature_vector.reshape((1, -1)), decodeData.reshape((1, -1)))[0][0]
                if distance >= 0.9:
                    list_book_similar.append(BookSimilarItem(
                        Id=book.Id,
                        Name=book.Name,
                        ThumbImage=book.ThumbImage,
                        Authors=book.Authors,
                        CreatedAt=book.CreatedAt,
                        UpdatedAt=book.UpdatedAt,
                        PublishedYear=book.PublishedYear,
                        PublishedBy=book.PublishedBy,
                        Status=book.Status,
                        distance=distance,
                    ))
                    
                logger.info(f"Id = {str(book.Id)} {book.Name} distance = " + str(distance))
    time_end = time.time()
    logger.info(f"check_feature_vector_all_exists_books time= {str(time_end - time_start)}")
    return list_book_similar

def get_draft_book_list_paging(page_index: int = 1, page_size: int = 20) -> DraftBookListResponse:    
    time_start = time.time()
    url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/DraftBooks?fields=Id%2CThumbImage%2CCreatedAt%2CUpdatedAt%2CStatus&sort=-UpdatedAt&where=where%3D%28Status%2Ceq%2CActive%29&limit={page_size}&offset={page_index - 1}"

    payload={}
    headers = {
        'accept': 'application/json',
        'xc-token': '5Bdhl77iJJ1fIbF2fPb8hcCceNzSJvmt4NIya0aR'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    list_draft_book : DraftBookListResponse = DraftBookListResponse.parse_raw(response.text)
    
    time_end = time.time()
    logger.info(f"get_draft_book_list_paging time= {str(time_end - time_start)}")
    return list_draft_book

def get_book_list_paging(page_index: int = 1, page_size: int = 20) -> BookListResponse:    
    time_start = time.time()
    url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/Books?fields=Id%2CName%2CAuthors%2CPublished%20Year%2CPublished%20By%2CStatus%2CThumbImage%2CBookCollections%20List%2CCreatedAt%2CUpdatedAt&sort=-UpdatedAt&where=where%3D%28Status%2Ceq%2CActive%29&limit={page_size}&offset={page_index-1}"

    payload={}
    headers = {
        'accept': 'application/json',
        'xc-token': '5Bdhl77iJJ1fIbF2fPb8hcCceNzSJvmt4NIya0aR'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    list_book : BookListResponse = BookListResponse.parse_raw(response.text)
    
    time_end = time.time()
    logger.info(f"get_book_list_paging time= {str(time_end - time_start)}")
    return list_book

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
    #logger.info(vec)
    pickled = pickle.dumps(vec)

    logger.info(f"length of {len(pickled)}")

    base64Data = codecs.encode(pickled, "base64").decode()

    logger.info(base64Data)

    decodeData = pickle.loads(codecs.decode(base64Data.encode(),'base64'))

    logger.info(f"length of {len(decodeData)}")
    #logger.info(decodeData)

    distance = cosine_similarity(vec.reshape((1, -1)), decodeData.reshape((1, -1)))[0][0]
    time_end = time.time()
    logger.info("distance = " + str(distance) + " time= " + str(time_end - time_start))

    img2 = Image.open('b02.jpg')
    vec2 = img2vec.get_vec(img2, tensor=True)

    distance2 = cosine_similarity(vec.reshape((1, -1)), vec2.reshape((1, -1)))[0][0]
    time_end = time.time()
    logger.info("distance2 = " + str(distance2) + " time= " + str(time_end - time_start))
    

    img3 = Image.open('b01_1.jpg')
    vec3 = img2vec.get_vec(img3, tensor=True)

    distance3 = cosine_similarity(vec.reshape((1, -1)), vec3.reshape((1, -1)))[0][0]
    time_end = time.time()
    logger.info(f"distance3 = {str(distance3)} time= {str(time_end - time_start)}")
    return {"message": "Hello World"}

def create_draft_book(result_upload, feature_vector_base64) -> DraftBook | None:
    try:
        logger.info(f'create_draft_book {result_upload}')
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
        return DraftBook.parse_raw(response.text)
    except Exception as e:
        logger.exception(f"create_draft_book: An exception was thrown! {e}")
        return None

def create_book(request: CreateNewBookRequest) -> Book | None:
    try:
        time_start = time.time()
        logger.info(f'create_book {request.json()}')
        url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/Books"
        
        # TODO thumbImage: get draft book detail from request.draft_book_id
        # TODO feature_vector_base64: get draft book detail from request.draft_book_id

        bookRequestToDb = BookRequestToDb(
            Authors=request.author,
            Name=request.name,
            PublishedBy=request.published_by,
            PublishedYear=request.published_year,
            ThumbImage=thumbImage,
            Thumb_Image_Feature_Vector=feature_vector_base64,
        )
        
        payload = bookRequestToDb.json()

        headers = {
            'accept': 'application/json',
            'xc-token': '5Bdhl77iJJ1fIbF2fPb8hcCceNzSJvmt4NIya0aR',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        logger.info(f'create_book response {str(response)}')
        time_end = time.time()
        logger.info("create_book time= " + str(time_end - time_start))
        return Book.parse_raw(response.text)
    except Exception as e:
        logger.exception(f"create_book: An exception was thrown! {e}")
        return None

def encode_base64_feature_vector(feature_vector) -> str:
    pickled = pickle.dumps(feature_vector)
    base64Data = codecs.encode(pickled, "base64").decode()
    return base64Data

def upload_file_image(file_name, file_contents, content_type):
    try:
        time_start = time.time()
        logger.info(f"upload_file_image: file_name {file_name} content_type {content_type}")
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
        logger.info(f"upload_file_image response {str(response_list)}")

        time_end = time.time()
        logger.info("upload_file_image time= " + str(time_end - time_start))
        return response_list
    except Exception as e:
        logger.exception(f"upload_file_image: An exception was thrown! {str(e)}")
        return None

@app.post("/upload")
async def upload_draft_image(
    file: Annotated[UploadFile, File()],
) -> CreateDraftBookResponse:
    try:
        time_start = time.time()
        contents = file.file.read()

        feature_vector = get_image_feature_vector(contents)
        feature_vector_base64 = encode_base64_feature_vector(feature_vector)
        list_book_similar = check_feature_vector_all_exists_books(feature_vector)

        response_upload_file = upload_file_image(file.filename, contents, file.content_type)
        
        result_create_draft_book: CreateDraftBook | None = None

        if response_upload_file:
            result_create_draft_book = create_draft_book(response_upload_file, feature_vector_base64)
        else:
            raise Exception("Upload draft book image error")

        time_end = time.time()
        logger.info("upload_draft_image time= " + str(time_end - time_start))   

        if result_create_draft_book:
            return CreateDraftBookResponse(
                draftBook=result_create_draft_book,
                listBookSimilar=list_book_similar.listBookSimilar,
            )

        raise Exception("Create draft book error")
    except Exception as e:
        logger.exception(f"upload_draft_image: An exception was thrown! {str(e)}")
        raise HTTPException(status_code=500, detail="Error: " + str(e))
    finally:
        file.file.close()

@app.get("/draft-books")
async def get_draft_books(page: int = 1, limit: int = 20) -> DraftBookListResponse:
    try:
        time_start = time.time()
        list_result: DraftBookListResponse = get_draft_book_list_paging(
            page_index=page - 1,
            page_size=limit,
        )
        time_end = time.time()
        logger.info("get_draft_books time= " + str(time_end - time_start))
        return list_result
    except Exception as e:
        logger.exception(f"get_draft_books: An exception was thrown! {str(e)}")
        return None
    
@app.get("/books")
async def get_books(page: int = 1, limit: int = 20) -> BookListResponse:
    try:
        time_start = time.time()
        list_result: BookListResponse = get_book_list_paging(
            page_index=page - 1,
            page_size=limit,
        )
        time_end = time.time()
        logger.info("get_books time= " + str(time_end - time_start))
        return list_result
    except Exception as e:
        logger.exception(f"get_books: An exception was thrown! {str(e)}")
        return None
    
    # 1. Add Model response for API create_draft_book
    # 2. API get draft book detail = respone of API create_draft_book
    # 3. API create book from draft book
    
    # base64_bytes = base64.b64encode(contents)
    # base64_message = base64_bytes.decode('utf8')
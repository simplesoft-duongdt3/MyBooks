import os
from typing import Annotated
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
import requests
import time
from datetime import datetime
from request_models import BookRequestToDb, CreateNewBookRequest
from response_models import ListBookVectorProductResponse, ListBookVectorProduct, VectorProduct, SimilarItem, Book, BookFromDb, BookListResponse, BookListResponseFromDb, BookSimilarItem, CreateDraftBookResponse, DraftBook, DraftBookFromDb, DraftBookListResponse, DraftBookListResponseFromDb

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from util import logger
import uvicorn
from vector_db import insert_list_vector_product, get_image_feature_vector_bytes, encode_base64_feature_vector_bytes, decode_feature_vector_base64_str, search_vectors, insert_vector_product


app = FastAPI()
api_endpoint = os.getenv("HOST_DB", "")
db_token = os.getenv("DB_TOKEN", "")
min_distance_images = float(os.getenv("IMAGE_MIN_DISTANCE", "0.8"))

def get_draft_book_detail_from_db(draft_book_id: int) -> DraftBookFromDb | None:
    time_start = time.time()
    url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/DraftBooks/{draft_book_id}"

    payload={}
    headers = {
        'accept': 'application/json',
        'xc-token': db_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    textResponse: str = response.text
    draft_book : DraftBookFromDb = DraftBookFromDb.parse_raw(textResponse)
    
    time_end = time.time()
    logger.info(f"get_draft_book_detail_from_db time= {str(time_end - time_start)}")
    
    return draft_book
        
def key_search_similar_books(book: BookSimilarItem):
    return book.distance


def convert_list_similar2_dict(list_item: list[SimilarItem], min_distance: float) -> dict[int, SimilarItem]:
    res_dict: dict[int, SimilarItem] = {}
    for i in range(0, len(list_item)):
        if list_item[i].similar_score >= min_distance:
            res_dict[list_item[i].book_id] = list_item[i]
    return res_dict

def check_feature_vector_all_exists_books(image_feature_vector: bytes) -> list[BookSimilarItem]:
    list_book_similar: list[BookSimilarItem] = []
    
    time_start = time.time()
    list_similar: list[SimilarItem] = search_vectors(topK=5, vector_bytes=image_feature_vector)
    logger.info(f'found list_similar = {list_similar}')

    dict_similar_item: dict[int, SimilarItem] = convert_list_similar2_dict(list_item=list_similar, min_distance=min_distance_images)
    if(len(dict_similar_item.keys()) == 0):
        return list_book_similar
    
    logger.info(f'found dict_similar_item = {dict_similar_item}')

    list_similar_id: list[str] = list(map(lambda item: str(item), dict_similar_item.keys()))
    in_ids_condition = '%2C'.join(list_similar_id)
    url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/Books?fields=Id%2CName%2CAuthors%2CPublishedYear%2CPublishedBy%2CStatus%2CThumbImage%2CBookCollectionsList%2CCreatedAt%2CUpdatedAt%2CThumbImageFeatureVector&sort=-UpdatedAt&where=%28Id%2Cin{in_ids_condition}%29"

    payload={}
    headers = {
        'accept': 'application/json',
        'xc-token': db_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    bookListDb: BookListResponseFromDb = BookListResponseFromDb.parse_raw(response.text)
    if bookListDb and bookListDb.list is not None:
        for book in bookListDb.list:
            if book.Id in dict_similar_item:
                book_similar = dict_similar_item[book.Id]
                distance: float = book_similar.similar_score

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
    logger.info(f'found list_book_similar = {list_book_similar}')

    time_end = time.time()
    logger.info(f"check_feature_vector_all_exists_books time= {str(time_end - time_start)}")

    list_book_similar.sort(reverse=True, key=key_search_similar_books)
    logger.info(f'found list_book_similar after sort by desc distance = {list_book_similar}')
    return list_book_similar

def get_draft_book_list_paging(page_index: int = 1, page_size: int = 20) -> DraftBookListResponse | None:    
    time_start = time.time()
    url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/DraftBooks?fields=Id%2CThumbImage%2CCreatedAt%2CUpdatedAt%2CStatus&sort=-UpdatedAt&where=where%3D%28Status%2Ceq%2CActive%29&limit={page_size}&offset={page_index - 1}"

    payload={}
    headers = {
        'accept': 'application/json',
        'xc-token': db_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    textResponse: str = response.text
    list_draft_book : DraftBookListResponseFromDb = DraftBookListResponseFromDb.parse_raw(textResponse)
    
    time_end = time.time()
    logger.info(f"get_draft_book_list_paging time= {str(time_end - time_start)}")
    
    if list_draft_book and list_draft_book.list is not None:
        result: list[DraftBook] = list(map(lambda item: item, list_draft_book.list))
        return DraftBookListResponse(
            draftBooks=result,
            paging=list_draft_book.pageInfo,
        )

def get_book_list_paging(page_index: int = 1, page_size: int = 20) -> BookListResponse | None:    
    time_start = time.time()
    url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/Books?fields=Id%2CName%2CAuthors%2CPublishedYear%2CPublishedBy%2CStatus%2CThumbImage%2CBookCollectionsList%2CCreatedAt%2CUpdatedAt&sort=-UpdatedAt&where=where%3D%28Status%2Ceq%2CActive%29&limit={page_size}&offset={page_index-1}"

    payload={}
    headers = {
        'accept': 'application/json',
        'xc-token': db_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    list_book : BookListResponseFromDb = BookListResponseFromDb.parse_raw(response.text)
    
    time_end = time.time()
    logger.info(f"get_book_list_paging time= {str(time_end - time_start)}")

    if list_book and list_book.list is not None:
        return BookListResponse(
            books=list(map(lambda item: item, list_book.list)),
            paging=list_book.pageInfo,
        )
    
def get_all_book_list_vector() -> ListBookVectorProduct | None:    
    time_start = time.time()
    url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/Books?fields=Id%2CName%2CAuthors%2CPublishedYear%2CPublishedBy%2CStatus%2CThumbImage%2CBookCollectionsList%2CCreatedAt%2CUpdatedAt%2CThumbImageFeatureVector&sort=-UpdatedAt&where=where%3D%28Status%2Ceq%2CActive%29&limit=2000&offset=0"
    payload={}
    headers = {
        'accept': 'application/json',
        'xc-token': db_token
    }
    
    response = requests.request("GET", url, headers=headers, data=payload)
    list_book : BookListResponseFromDb = BookListResponseFromDb.parse_raw(response.text)
    logger.info(f"get_book_list_vector list_book= {len(list_book.list)}")
    
    listBookVectorProduct: list[VectorProduct] = []

    if list_book and list_book.list is not None:
        for book in list_book.list:
            if book.ThumbImageFeatureVector and len(book.ThumbImageFeatureVector) > 0:
                listBookVectorProduct.append(
                    VectorProduct(
                        product_id=book.Id,
                        product_vector_bytes=decode_feature_vector_base64_str(book.ThumbImageFeatureVector),
                    )
                )
    logger.info(f"get_book_list_vector listBookVectorProduct= {len(listBookVectorProduct)}")
    time_end = time.time()
    logger.info(f"get_book_list_vector time= {str(time_end - time_start)}")
    return ListBookVectorProduct(
        listBookVectorProduct=listBookVectorProduct,
    )

def create_draft_book(result_upload, feature_vector_base64) -> DraftBook | None:
    try:
        logger.info(f'create_draft_book {result_upload}')
        url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/DraftBooks"

        payload = json.dumps({
            "ThumbImage": result_upload,
            "ThumbImageFeatureVector": feature_vector_base64
        })
        headers = {
            'accept': 'application/json',
            'xc-token': db_token,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return DraftBookFromDb.parse_raw(response.text)
    except Exception as e:
        logger.exception(f"create_draft_book: An exception was thrown! {e}")
        return None

@app.post('/books')
def create_book(request: CreateNewBookRequest) -> Book | None:
    try:
        time_start = time.time()
        logger.info(f'create_book {request.json()}')
        url = f"{api_endpoint}/api/v1/db/data/v1/MyBooks/Books"
        
        draft_book = get_draft_book_detail_from_db(draft_book_id=request.DraftBookId)
        # TODO thumbImage: get draft book detail from request.draft_book_id
        # TODO feature_vector_base64: get draft book detail from request.draft_book_id

        if not draft_book:
            logger.exception(f"create_book: Not found draft book. draft_book_id: {request.DraftBookId}")
            return None

        image_vector_base64_str = draft_book.ThumbImageFeatureVector

        bookRequestToDb = BookRequestToDb(
            Authors=request.Authors,
            Name=request.Name,
            PublishedBy=request.PublishedBy,
            PublishedYear=request.PublishedYear,
            ThumbImage=draft_book.ThumbImage,
            ThumbImageFeatureVector=image_vector_base64_str,
        )
        
        payload = bookRequestToDb.json()

        headers = {
            'accept': 'application/json',
            'xc-token': db_token,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        logger.info(f'create_book response {str(response)}')
        time_end = time.time()
        logger.info("create_book time= " + str(time_end - time_start))
        
            
        book_inserted = BookFromDb.parse_raw(response.text)
        
        # insert into vector db
        insert_vector_product(
            product_id=book_inserted.Id,
            product_vector_bytes=decode_feature_vector_base64_str(image_vector_base64_str),
        )
        return book_inserted
    except Exception as e:
        logger.exception(f"create_book: An exception was thrown! {e}")
        return None

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
            'xc-token': db_token
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

        feature_vector: bytes = get_image_feature_vector_bytes(file_bytes=contents)
        feature_vector_base64: str = encode_base64_feature_vector_bytes(feature_vector)
        list_book_similar: list[BookSimilarItem] = check_feature_vector_all_exists_books(feature_vector)

        response_upload_file = upload_file_image(file.filename, contents, file.content_type)
        
        result_create_draft_book: DraftBook | None = None

        if response_upload_file:
            result_create_draft_book = create_draft_book(response_upload_file, feature_vector_base64)
        else:
            raise Exception("Upload draft book image error")

        time_end = time.time()
        logger.info("upload_draft_image time= " + str(time_end - time_start))   

        if result_create_draft_book:
            return CreateDraftBookResponse(
                draftBook=result_create_draft_book,
                listBookSimilar=list_book_similar,
            )

        raise Exception("Create draft book error")
    except Exception as e:
        logger.exception(f"upload_draft_image: An exception was thrown! {str(e)}")
        raise HTTPException(status_code=500, detail="Error: " + str(e))
    finally:
        file.file.close()

@app.get("/draft-books")
async def get_draft_books(page: int = 1, limit: int = 20) -> DraftBookListResponse | None:
    try:
        logger.info(f"get_draft_books start page {page} limit {limit}")
        time_start = time.time()
        list_result: DraftBookListResponse | None = get_draft_book_list_paging(
            page_index=page,
            page_size=limit,
        )
        time_end = time.time()
        logger.info("get_draft_books time= " + str(time_end - time_start))
        return list_result
    except Exception as e:
        logger.exception(f"get_draft_books: An exception was thrown! {str(e)}")
        return None
    
@app.get("/books")
async def get_books(page: int = 1, limit: int = 20) -> BookListResponse | None:
    try:
        time_start = time.time()
        list_result: BookListResponse | None = get_book_list_paging(
            page_index=page,
            page_size=limit,
        )
        time_end = time.time()
        logger.info("get_books time= " + str(time_end - time_start))
        return list_result
    except Exception as e:
        logger.exception(f"get_books: An exception was thrown! {str(e)}")
        return None
    
@app.post("/update-books-vector")
async def update_books_vector() -> ListBookVectorProductResponse | None:
    try:
        time_start = time.time()
        list_result: ListBookVectorProduct | None = get_all_book_list_vector()
        if list_result:
            insert_list_vector_product(list_vector_product=list_result.listBookVectorProduct)

        time_end = time.time()
        list_id: list[int] = list(map(lambda item: item.product_id, list_result.listBookVectorProduct))
        logger.info("get update_books_vector time= " + str(time_end - time_start))
        
        return ListBookVectorProductResponse(list_id=list_id) 
    except Exception as e:
        logger.exception(f"update_books_vector: An exception was thrown! {str(e)}")
        return None
    
@app.get("/draft_books/{id}")
async def get_draft_book_detail(id: int) -> CreateDraftBookResponse | None:
    try:
        time_start = time.time()
        draft_book: DraftBookFromDb | None = get_draft_book_detail_from_db(
            draft_book_id=id,
        )
        response: CreateDraftBookResponse | None = None
        list_book_similar: list[BookSimilarItem] = []
        if draft_book and draft_book.ThumbImageFeatureVector:
            feature_vector_bytes = decode_feature_vector_base64_str(draft_book.ThumbImageFeatureVector)
            list_book_similar = check_feature_vector_all_exists_books(feature_vector_bytes)
            response = CreateDraftBookResponse(
                draftBook=draft_book,
                listBookSimilar=list_book_similar,
            )
        
        time_end = time.time()
        logger.info("get_books time= " + str(time_end - time_start))
        return response
    except Exception as e:
        logger.exception(f"get_draft_book_detail: An exception was thrown! {str(e)}")
        return None
    # 1. Add Model response for API create_draft_book
    # 2. API get draft book detail = respone of API create_draft_book
    # 3. API create book from draft book
    
    # base64_bytes = base64.b64encode(contents)
    # base64_message = base64_bytes.decode('utf8')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
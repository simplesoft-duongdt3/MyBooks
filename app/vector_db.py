import base64
import os
import numpy as np
from redis import Redis
from redis.exceptions import ResponseError
from redis.commands.search.field import VectorField
from redis.commands.search.field import TextField
from redis.commands.search.field import NumericField
from redis.commands.search.query import Query
from PIL import Image
from img2vec_pytorch import Img2Vec
import io
from response_models import SimilarItem
from util import logger
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from dotenv import load_dotenv
load_dotenv()

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "10001"))

INDEX_NAME='BOOK_INDEX'
IMAGE_VECTOR_DIMENSION = 2048
PRODUCT_IMAGE_VECTOR_FIELD = 'image_image_vector'
PRODUCT_ID_FIELD = 'id'
NUMBER_PRODUCTS = 1000
DISTANCE_METRIC = 'COSINE'
img2vec = Img2Vec(cuda=False, model='resnet152')

redis_conn = Redis(
    host = redis_host, port = redis_port, 
    encoding="utf-8",
    decode_responses=False,
)

# redis_conn.flushall()

def create_flat_index (redis_conn: Redis, index_name: str, vector_field_name: str, id_field_name: str, number_of_vectors: int, vector_dimensions: int=512, distance_metric: str='L2'):
    try:
        search = redis_conn.ft(index_name= index_name)
        # index_info = search.info()
        # logger.info(f'index_info {index_info}')
        search.create_index([
            VectorField(vector_field_name, "FLAT", {"TYPE": "FLOAT32", "DIM": vector_dimensions, "DISTANCE_METRIC": distance_metric, "INITIAL_CAP": number_of_vectors, "BLOCK_SIZE":number_of_vectors }),
            NumericField(id_field_name),     
        ])
    except ResponseError as e:
        logger.exception('Redis create_flat_index')


def insert_vector_product(product_id: int, product_vector_bytes: bytes, id_field_name: str = PRODUCT_ID_FIELD, vector_field_name: str = PRODUCT_IMAGE_VECTOR_FIELD, redis_conn: Redis = redis_conn):
    item_metadata = {
        id_field_name : product_id,
        vector_field_name: product_vector_bytes,
    }
    redis_conn.hset(f'{product_id}', mapping=item_metadata)

def search_vectors(topK: int, vector_bytes: bytes) -> list[SimilarItem]:
    listSimilarItem: list[SimilarItem] = []
    #prepare the query
    q = Query(f'*=>[KNN {topK} @{PRODUCT_IMAGE_VECTOR_FIELD} $vec_param AS vector_score]').sort_by('vector_score').paging(0,topK).return_fields('vector_score', PRODUCT_ID_FIELD).dialect(2)
    params_dict = {"vec_param": vector_bytes}

    #Execute the query
    results = redis_conn.ft(index_name=INDEX_NAME).search(q, query_params = params_dict)
    # docs = redis_conn.ft(index_name=INDEX_NAME).search(q,params_dict).docs

    logger.info('***************Product  found ************')
    #Print similar products found
    for product in results.docs:
        logger.info(f'Product found item: {product}')
        product_id: int = int(product[PRODUCT_ID_FIELD])
        similar_score: float = 1.0 - float(product['vector_score'])
        listSimilarItem.append(SimilarItem(
            similar_score=similar_score,
            book_id=product_id,
        ))
    return listSimilarItem

def get_image_feature_vector_bytes(file_bytes: bytes, img2vec: Img2Vec=img2vec) -> bytes:
    # Read in an image (rgb format)
    img = Image.open(io.BytesIO(file_bytes))
    # Get a vector from img2vec, returned as a Numpy ndarray
    vec = img2vec.get_vec(img, tensor=False)
    vector_float32 = vec.astype(np.float32)
    vector_bytes = vector_float32.tobytes()
    return vector_bytes

def encode_base64_feature_vector_bytes(feature_vector_bytes: bytes) -> str:
    base64_bytes = base64.b64encode(feature_vector_bytes)
    base64_message = base64_bytes.decode()
    return base64_message

def decode_feature_vector_base64_str(feature_vector_base64_str: str) -> bytes:
    base64_bytes = feature_vector_base64_str.encode()
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes

# Init index here
create_flat_index(
    id_field_name=PRODUCT_ID_FIELD,
    vector_field_name=PRODUCT_IMAGE_VECTOR_FIELD,
    distance_metric=DISTANCE_METRIC,
    number_of_vectors=NUMBER_PRODUCTS,
    redis_conn=redis_conn,
    vector_dimensions=IMAGE_VECTOR_DIMENSION,
    index_name=INDEX_NAME,
)


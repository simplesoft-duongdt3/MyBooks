import codecs
import base64
import random
import numpy as np
# import pandas as pd
import time
from redis import Redis
from redis.commands.search.field import VectorField
from redis.commands.search.field import TextField
from redis.commands.search.field import TagField
from redis.commands.search.query import Query
from PIL import Image
from img2vec_pytorch import Img2Vec
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# Initialize Img2Vec without GPU
# resnet152 2048
# gen 3 vector time= 0.3303859233856201
# insert + search redis 3 vector time= 0.011393070220947266
# gen 3 vector time= 0.30896997451782227
# insert + search redis 3 vector time= 0.014062166213989258
# gen 3 vector time= 0.3175818920135498
# insert + search redis 3 vector time= 0.007185220718383789

# resnet18 512
# gen 3 vector time= 0.10181188583374023
# insert + search redis 3 vector time= 0.01618027687072754
# gen 3 vector time= 0.07336091995239258
# insert + search redis 3 vector time= 0.02003312110900879
# gen 3 vector time= 0.09581732749938965
# insert + search redis 3 vector time= 0.014796733856201172


# efficientnet_b0 1280
# gen 3 vector time= 0.6501989364624023
# insert + search redis 3 vector time= 0.01497340202331543
# gen 3 vector time= 0.6362099647521973
# insert + search redis 3 vector time= 0.014306068420410156
# gen 3 vector time= 0.6546528339385986
# insert + search redis 3 vector time= 0.013219118118286133

# efficientnet_b7 2560
# gen 3 vector time= 4.143211841583252
# insert + search redis 3 vector time= 0.013882875442504883
# gen 3 vector time= 4.154558897018433
# insert + search redis 3 vector time= 0.014590024948120117
# gen 3 vector time= 4.071782112121582
# insert + search redis 3 vector time= 0.013045072555541992

IMAGE_VECTOR_DIMENSION = 2048
img2vec = Img2Vec(cuda=False, model='resnet152')

host = 'localhost'
port = 10001
redis_conn = Redis(
    host = host, port = port, 
    encoding="utf-8",
    decode_responses=False,
    )

def create_flat_index (redis_conn,vector_field_name,number_of_vectors, vector_dimensions=512, distance_metric='L2'):
    redis_conn.ft().create_index([
        VectorField(vector_field_name, "FLAT", {"TYPE": "FLOAT32", "DIM": vector_dimensions, "DISTANCE_METRIC": distance_metric, "INITIAL_CAP": number_of_vectors, "BLOCK_SIZE":number_of_vectors }),
        TagField("id"),
        TextField("name"),       
    ])

def get_image_feature_vector(file_path):
    # Read in an image (rgb format)
    img = Image.open(file_path)
    # Get a vector from img2vec, returned as a torch FloatTensor
    vec = img2vec.get_vec(img, tensor=False)
    return vec

PRODUCT_IMAGE_VECTOR_FIELD = 'image_image_vector'
NUMBER_PRODUCTS = 1000

DISTANCE_METRIC = 'COSINE'

def insert_redis(redis_conn, id, vector_bytes):
    item_metadata = {
        'id' : f'{id}',
        'name' : f'Image {id}',
        PRODUCT_IMAGE_VECTOR_FIELD: vector_bytes,
    }
    redis_conn.hset(f'{id}',mapping=item_metadata)

if __name__ == "__main__":
    print ('Connecting to redis')
    redis_conn.ping()
    print ('Connected to redis')
    redis_conn.flushall()

    create_flat_index(redis_conn, PRODUCT_IMAGE_VECTOR_FIELD,NUMBER_PRODUCTS,IMAGE_VECTOR_DIMENSION,DISTANCE_METRIC)

    time_start = time.time()
    
    vector = get_image_feature_vector('test01.jpg')
    # print(type(vector))
    # print(len(vector))
    # print(vector.shape)
    # print(vector)

    vector_float32 = vector.astype(np.float32)
    # print(type(vector_float32))
    # print(len(vector_float32))
    # print(vector_float32.shape)
    # print(vector_float32)

    vector_bytes = vector_float32.tobytes()
    # Encode 1
    # base64_bytes = base64.b64encode(vector_bytes)
    # base64_message = base64_bytes.decode()

    # print(f'base64_message 1 {base64_message}')

    # Decode
    # base64_bytes = base64_message.encode()
    # message_bytes = base64.b64decode(base64_bytes)

    # Encode 2
    # base64_bytes = base64.b64encode(message_bytes)
    # base64_message = base64_bytes.decode()

    # print(f'base64_message 2 {base64_message}')


    vector_verify = get_image_feature_vector('test01_verify.jpg')
    vector_verify_float32 = vector_verify.astype(np.float32)
    vector_verify_bytes = vector_verify_float32.tobytes()

    vector_verify2 = get_image_feature_vector('test01_verify2.jpg')
    vector_verify2_float32 = vector_verify2.astype(np.float32)
    vector_verify2_bytes = vector_verify2_float32.tobytes()

    time_end = time.time()
    print("gen 3 vector time= " + str(time_end - time_start))

    # item_metadata = {
    #     'id' : '001',
    #     'name' : 'Image 001',
    #     PRODUCT_IMAGE_VECTOR_FIELD: vector_bytes,
    # }
    # redis_conn.hset('001',mapping=item_metadata)
    time_start = time.time()

    insert_redis(redis_conn, '001', vector_bytes)
    insert_redis(redis_conn, '002', vector_verify_bytes)
    insert_redis(redis_conn, '003', vector_verify2_bytes)
    # For multi records
    # p = redis_conn.pipeline(transaction=False)
    # p.hset('001',mapping=item_metadata)


    print(f'Keys redis size {len(redis_conn.keys())}')

    topK=5
    query_vector = vector_verify2_bytes

    #prepare the query
    q = Query(f'*=>[KNN {topK} @{PRODUCT_IMAGE_VECTOR_FIELD} $vec_param AS vector_score]').sort_by('vector_score').paging(0,topK).return_fields('vector_score','id','name').dialect(2)
    params_dict = {"vec_param": query_vector}

    #Execute the query
    results = redis_conn.ft().search(q, query_params = params_dict)
    docs = redis_conn.ft().search(q,params_dict).docs

    #Print similar products found
    for product in results.docs:
        print ('***************Product  found ************')
        print(product)
    
    time_end = time.time()
    print("insert + search redis 3 vector time= " + str(time_end - time_start))






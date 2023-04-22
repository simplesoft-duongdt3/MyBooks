import random
import numpy as np
import pandas as pd
import time
from redis import Redis
from redis.commands.search.field import VectorField
from redis.commands.search.field import TextField
from redis.commands.search.field import TagField
from redis.commands.search.query import Query
from PIL import Image
from img2vec_pytorch import Img2Vec

# Initialize Img2Vec without GPU
img2vec = Img2Vec(cuda=False, model='resnet18')

host = 'localhost'
port = 6379
redis_conn = Redis(host = host, port = port)

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
IMAGE_VECTOR_DIMENSION = 512
DISTANCE_METRIC = 'COSINE'

if __name__ == "__main__":
    print ('Connecting to redis')
    redis_conn.ping()
    print ('Connected to redis')
    redis_conn.flushall()
    
    create_flat_index(redis_conn, PRODUCT_IMAGE_VECTOR_FIELD,NUMBER_PRODUCTS,IMAGE_VECTOR_DIMENSION,DISTANCE_METRIC)


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
    # print(type(vector_bytes))
    # print(len(vector_bytes))
    # print(vector_bytes)
    item_metadata = {
        'id' : '001',
        'name' : 'Image 001',
        PRODUCT_IMAGE_VECTOR_FIELD: vector_bytes,
    }
    p = redis_conn.pipeline(transaction=False)
    p.hset('001',mapping=item_metadata)


    topK=5
    query_vector = vector_bytes

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
    






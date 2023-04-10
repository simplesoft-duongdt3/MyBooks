from fastapi import FastAPI
import time
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

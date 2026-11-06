from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  

vec = model.encode("A dog is sleeping near the couch")
print(vec.shape)
print(vec[:5])
print(len(vec))

from numpy import dot
from numpy.linalg import norm

v1 = model.encode("A Cat is trying to drink milk from the bowl near the couch")
v2 = model.encode("A kitten is trying to drick milk near the couch")

similarity =  dot(v1,v2) / (norm(v1) * norm(v2))
print(similarity)
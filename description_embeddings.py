from sentence_transformers import SentenceTransformer
import json
import numpy as np

print("loaded libraries")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("loaded model")

with open("output/google_books.json", 'r') as f:
    google_books: dict = json.load(f)
    
descriptions = []

for key in google_books.keys():
    try:
        descriptions.append(google_books[key]["volumeInfo"]["description"])
    except:
        print("error")


print("encoding")
embeddings = model.encode(descriptions)

np.save("output/Description_Embeddings.npy", embeddings)
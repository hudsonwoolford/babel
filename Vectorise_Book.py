import numpy as np
import json


def extract_categories(book: dict) -> set:
    result = set()
    categories = book["volumeInfo"]["categories"]

    for c in categories:
        items = c.strip().split(" / ")
        
        for it in items:
            result.add(it)
    
    return result


if __name__ == "__main__":

    # with open("output/google_books_cleaned.json", "r", encoding="utf-8") as f:
    #     book_data = json.load(f)

    #     all_categories = dict()
    #     cat_num = 0
    #     keys = list(book_data.keys())
    #     for key in keys:
    #         try:
    #             local_categories = extract_categories(book_data[key])
    #             for cat in local_categories:
    #                 if cat not in all_categories.keys():
    #                     all_categories[str(cat)] = cat_num
    #                     cat_num += 1
    #         except:
    #             print("Corrupted book, key: ", key)

    #     print(all_categories)

    # vecs = np.zeros((len(keys),len(list(all_categories.keys()))))

    # for i, key in enumerate(keys):
    #     try:
    #         categories = extract_categories(book_data[key])
    #         for cat in categories:
    #             vecs[i, all_categories[str(cat)]] = 1
    #     except:
    #         print("Corrupted book, key: ", key)

    # np.save("output/book_vectors.npy", vecs)

    vecs = np.load("output/book_vectors.npy")

    index = int(input("Index: "))

    sim = np.zeros(len(vecs))
    for i in range(len(vecs)):
        cos_sim = np.dot(vecs[index], vecs[i]) / (np.linalg.norm(vecs[index]) * np.linalg.norm(vecs[i]))
        sim[i]= cos_sim

    ranked = np.argsort(sim)

    with open("output/google_books_cleaned.json", "r", encoding="utf-8") as f:
        book_data = json.load(f)

    for i in range(10):
        book = book_data[str(ranked[i] + 1)]

        print(book["volumeInfo"]["title"])
        print(book["volumeInfo"]["authors"])
        print(book["volumeInfo"]["categories"])
        print(book["volumeInfo"]["description"][:50])
        print("\n")
    
    


            
        


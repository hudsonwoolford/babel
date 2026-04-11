import pandas as pd
import json
import numpy as np
import random

def get_catalog_df(path: str):
    return pd.read_csv("pg_catalog.csv")

def parse_categories(bookshelve: str) -> set:
    categories = set()

    cat_1 = bookshelve.strip().split("; ")
    for cat_2 in cat_1:
        categories.add(cat_2.removeprefix("Category: "))

    return categories

def save_categories(df: pd.DataFrame):
    categories = set()
    for bookshelve in df.Bookshelves:
        categories = categories | parse_categories(str(bookshelve))

    with open("output/categories.txt", 'w', encoding='utf-8') as f:
        f.write("\n".join(list(categories)))

def save_book_list(df: pd.DataFrame):
    with open("output/book_list.txt", 'a', encoding='utf-8') as f:
        for title in df.Title:
            if len(title) != 0:
                f.write(f"{title.strip()}")

def save_book_vectors(df: pd.DataFrame):
    category_map = {}
    with open("input/categories.txt", "r", encoding="utf-8") as f:
        for i, category in enumerate(f.readlines()):
            category_map[str(category.strip())] = i
    
    d = len(category_map.keys())

    vectors = []
    for bookshelve in df.Bookshelves:
        vec = np.zeros(d)
        categories = parse_categories(str(bookshelve))
        for category in categories:
            vec[category_map[str(category)]] = 1
        
        vectors.append(vec)
    
    np.save("output/book_vectors.npy",np.stack(vectors))

def most_similar(user, vectors, banned):

    max_i = 0
    max_sim = 0
    for i in range(len(vectors)):
        if i in banned:
            continue

        sim = np.dot(user, vectors[i]) / (np.linalg.norm(user) * np.linalg.norm(vectors[i]))

        if sim > max_sim:
            max_i = i
            max_sim = sim
    
    return max_i

books =  get_catalog_df("pg_catalog.csv").Title[:5000]
subjects =  get_catalog_df("pg_catalog.csv").Subjects[:5000]
vectors = np.load("input/book_vectors.npy")[:5000]
all_rec = []
banned = []
while True:
    if len(all_rec) > 0:
        average = np.average(np.stack(all_rec), axis=0)
        rec_book = most_similar(average, vectors, banned)
    else:
        rec_book = random.choice(range(len(vectors)))

    banned.append(rec_book)
    print(books[rec_book], subjects[rec_book])
    choice = input("y/n: ")
    if choice == "y":
        all_rec.append(vectors[rec_book])


# df = get_catalog_df("pg_catalog.csv")
# save_book_vectors(df)
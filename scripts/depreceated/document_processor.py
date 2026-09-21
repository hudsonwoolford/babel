import json
import numpy as np
from tokeniser import tokenise

# for BM25:
# f(q, D) - number of times keyword q appears in document D (gonna just set to 1 bc kinda useless for documents as short as a title (maybe the?))
# n(q) - number of documents containing keyword
# |D| - length of document
# avgdl - average document length
# N - total documents in the collection
# k e [1.2, 2.0], b e [0.75]

def get_ids():
    with open("output/book_data.json") as f:
        book_list = json.load(f)["data"]["books"]
    
    d_id = [b.get("id", "") for b in book_list]
    return d_id

def get_titles():
    with open("output/book_data.json") as f:
        book_list = json.load(f)["data"]["books"]
    
    titles = [b.get("title", "") for b in book_list]
    return titles

def process_documents(documents: list, ids: list):

    N = len(documents)
    data = {
        "term_data": {},
        "doc_data": {},
        "avg_dl": -1,
        "N": N,
    }

    total_n_terms = 0
    for i in range(N):
        terms = set(tokenise(documents[i]))

        #doc length
        data["doc_data"][ids[i]] = len(terms)
        total_n_terms += len(terms)

        #term frequencies

        for term in terms:
            post_list = data["term_data"].get(term, [])
            post_list.append(ids[i])
            data["term_data"][term] = post_list
    
    data["avg_dl"] = total_n_terms / N
    
    return data
    

def  main():
    documents = get_titles()
    ids = get_ids()

    data = process_documents(documents, ids)

    with open("output/doc_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)

if __name__ == "__main__":
    main()


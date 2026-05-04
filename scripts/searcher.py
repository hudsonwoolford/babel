import numpy as np
from tokeniser import tokenise
import json
import re

class BM25:
    def __init__(self,
                 term_data: dict,
                 doc_data: dict,
                 k: float, 
                 b: float):
        
        self.term_data = term_data
        self.doc_data = doc_data

        self.k = k
        self.b = b

        self.N = len(doc_data)
        self.avg_dl = np.mean(list(doc_data.values()))

    # inverse document frequency
    def inverse_df(self, n_q: int):
        numer = self.N - n_q + 0.5
        denom = n_q + 0.5 #cannot be zero?
        
        return np.log(numer / denom + 1)
    
    # term frequency
    def term_f(self, freq: int, d_length: int):
        numer = self.k * freq
        denom = freq + self.k * (1 - self.b + self.b * (d_length / self.avg_dl))
        denom = 1 if denom == 0 else denom
        return numer / denom
    
    def score(self, keywords: list, doc_id: int):
        
        keyword_weights = []
        d_length = self.doc_data[str(doc_id)] #number of terms in document
        for kw in keywords:
            docs_containing = self.term_data.get(kw, [])
            n_q = len(docs_containing) #number of documents containing keyword
            if n_q == 0:
                continue

            in_doc = doc_id in set(docs_containing)

            inverse_doc = self.inverse_df(n_q)
            term_freq = self.term_f(int(in_doc), d_length)

            keyword_weights.append(inverse_doc * term_freq)

        return np.sum(keyword_weights)

    def rank(self, query: str):
        keywords = tokenise(query)

        doc_ids = np.array(list(self.doc_data.keys()), dtype=int)
        scores = [self.score(keywords, doc_id) for doc_id in doc_ids]
        sorted_args = np.argsort(scores)[::-1]

        return doc_ids[sorted_args]

class Soundex:

    def __init__(self):
        pass

    def encode(self, text: str):
        # Drop duplicate letters, except for c.
        text = re.sub(r"([a-bd-z])\1", r"\1", text, flags=re.IGNORECASE)

        # If the word begins with 'KN', 'GN', 'PN', 'AE', 'WR', drop the first letter.
        text = re.sub(r"\b(:)(*)", r"\1", text, flags=re.IGNORECASE)

if __name__ == "__main__":
    # with open("output/id_mapping.json") as f:
    #     id_2_index = json.load(f)

    # with open("output/book_data.json") as f:
    #     book_list = json.load(f)["data"]["books"]
    
    # with open("output/doc_data.json") as f:
    #     doc_data = json.load(f)

    # searcher = BM25(doc_data["term_data"], doc_data["doc_data"], k=1.5, b=0.75)
    
    metaphone = Soundex()
    print(metaphone.encode("accent"))
    print(metaphone.encode("impossible"))
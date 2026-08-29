import numpy as np
from tokeniser import tokenise
import json
import re
import time

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

class Levenshtein:
    # tokenize queries and titles
    # check for token matches using fuzzy matching
    #   -> first letter match
    #   -> length ratio > 0.5
    #   -> finally levenstein
    # those with higher scores pass
    # final levenstein distance calculation
    def __init__(self, options: list):
        self.options = np.array(options)

    def fuzzy_match(self, w1: str, w2: str,
                    min_length: int = 3,
                    min_length_ratio: float = 0.75,
                    min_lsim: float = 0.75,
                    first_letter: bool = True):
        
        min_len = min(len(w1), len(w2))

        #length barrier
        if min_len < min_length:
            return False

        #first letter barrier
        if first_letter and w1[0] != w2[0]:
            return False

        #length ratio barrier
        max_len = max(len(w1), len(w2))
        length_ratio = min_len / max_len
        if length_ratio < min_length_ratio:
            return False
        
        #levenshtein distance barrier
        norm_dist = 1 - self.ldistance(w1, w2) / max_len
        if norm_dist < min_lsim:
            return False
        
        #passed all barriers
        return True

    def coarse_filter(self, a: str, b: str):
        a_words = tokenise(a)
        b_words = tokenise(b)

        matches = 0
        for b_w in b_words:
            for a_w in a_words:
                matches += 1 if self.fuzzy_match(a_w, b_w) else 0

        checks = len(b_words) * len(a_words)
        checks = 1 if checks == 0 else checks

        curved_checks = 2 / (1 + np.exp(-(checks-1)))

        return matches / curved_checks

    def sliding_lsim(self, a: str, b: str):
        b_words = tokenise(b)
        
        best = -1

        #get every possible sub-array
        for i in range(len(b_words)):
            for j in range(i+1, len(b_words)+1):
                sub_text = ' '.join(b_words[i:j])
                similarity = 1 - self.ldistance(sub_text, a) / max(len(a), len(sub_text))
                best = max(best, similarity)
        
        return best


    def ldistance(self, a: str, b: str) -> int:
        """Calculates the Levenshtein (edit) distance between two strings with matrices

        Args:
            a (str): string 1
            b (str): string 2

        Returns:
            int: number of edits required
        """        
        #check already equal
        if a == b: 
            return 0
        
        l_a = len(a)
        l_b = len(b)

        #l_a + 1 rows and l_b + 1 columns
        matrix = np.zeros((l_a+1, l_b+1), dtype=int)
        
        matrix[0] = np.arange(l_b+1)
        matrix[:, 0] = np.arange(l_a+1)

        for x in range(1, l_a + 1):
            for y in range(1, l_b + 1):

                if a[x-1] == b[y-1]:
                    matrix[x, y] = matrix[x-1, y-1]
                else:
                    matrix[x, y] = 1 + min(matrix[x-1, y], 
                                            matrix[x-1, y-1], 
                                            matrix[x, y-1])
        
        return matrix[-1, -1]

    def search(self, query: str, coarse_size: int = 200, final_size: int = 10):

        #coarse filter for naive matches
        matches = np.zeros(len(self.options))
        for i in range(len(matches)):
            matches[i] = self.coarse_filter(query, self.options[i])

        top_matches = np.argsort(matches)[::-1][:coarse_size]
        search_space = self.options[top_matches]

        #fine filter for exact matches
        similarities = np.zeros(len(search_space))
        for i in range(len(similarities)):
            similarities[i] = self.sliding_lsim(query, search_space[i])

        top_sims = np.argsort(similarities)[::-1][:final_size]
        return top_matches[top_sims] #return indices of top matches 




if __name__ == "__main__":
    with open("output/id_mapping.json") as f:
        id_2_index = json.load(f)

    with open("output/book_data.json") as f:
        book_list = json.load(f)["data"]["books"]

    book_titles = np.array([book["title"].lower() for book in book_list], dtype=str)
    del book_list
    
    # with open("output/doc_data.json") as f:
    #     doc_data = json.load(f)

    # searcher = BM25(doc_data["term_data"], doc_data["doc_data"], k=1.5, b=0.75)
    
    levenshtein = Levenshtein()
    while True:
        search_query = input("Search: ").lower()
        top_n = levenshtein.search(search_query, book_titles)

        
        print(book_titles[top_n])

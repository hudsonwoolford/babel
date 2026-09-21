import numpy as np
from tokeniser import tokenise
import json
import re
import time

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
        self.tokens = [tokenise(o) for o in options]

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
        norm_dist = 1 - Levenshtein.ldistance(w1, w2) / max_len
        if norm_dist < min_lsim:
            return False
        
        #passed all barriers
        return True

    def coarse_filter(self, q_words, b_words):
        if not q_words or not b_words:
            return 0

        q_hits = set()
        b_hits = set()
        for i, q_w in enumerate(q_words):
            for j, b_w in enumerate(b_words):
                if self.fuzzy_match(q_w, b_w):
                    q_hits.add(i)
                    b_hits.add(j)

        #prevent division by zero
        q_length = len(q_words) if len(q_words) != 0 else 1
        b_length = len(b_words) if len(b_words) != 0 else 1

        return len(q_hits) / q_length + 0.1 * len(b_hits) / b_length

    def sliding_lsim(self, q_words, b_words):
        if not q_words or not b_words:
            return 0

        shorter, longer = sorted((q_words,b_words), key=len)
        short_sub = ' '.join(shorter)
        n_short = len(shorter)

        best = 0
        #check substrings similar to shorter
        for window_size in range(n_short-1, n_short+2):
            for i in range(len(longer)-window_size+1):
                window = ' '.join(longer[i:i+window_size])
                distance = Levenshtein.ldistance(short_sub, window)
                similarity = 1 - distance / max(len(window), len(short_sub))
                best = max(best, similarity)
        
        return best

    @staticmethod
    def ldistance(a: str, b: str) -> int:
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
        q_words = tokenise(query)

        #coarse filter for naive matches
        coarse = np.array([self.coarse_filter(q_words, tokenised) for tokenised in self.tokens])
        top_coarse = np.argsort(coarse)[::-1][:coarse_size]

        #fine filter for exact matches
        fine = np.array([self.sliding_lsim(q_words, self.tokens[i]) for i in top_coarse])
        final = 0.75 * fine + 0.25 * coarse[top_coarse]

        order = np.argsort(final)[::-1][:final_size]
        return top_coarse[order] 




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

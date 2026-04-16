import numpy as np
import vector_utils
from sklearn.preprocessing import StandardScaler    
from sklearn.preprocessing import normalize    
import json


class Rocchio:
    def __init__(self, book_vectors: np.ndarray):

        self.book_vectors = book_vectors
        self.liked_vectors = []
        self.disliked_vectors = []
        self.user_vector = np.zeros(book_vectors.shape[1])
    
    def score(self, vec_1: np.ndarray, vec_2: np.ndarray):
        return vector_utils.cosine_similarity(vec_1, vec_2)

    def recommend(self, seen_indices: set):
        scores = []
        candidate_indices = []
        for i in range(len(self.book_vectors)):
            if i in seen_indices:
                continue

            scores.append(self.score(self.user_vector, self.book_vectors[i]))
            candidate_indices.append(i)
        
        return candidate_indices[np.argmax(scores)]
    
    def update(self, index: int, liked: bool):
        if liked:
            self.liked_vectors.append(self.book_vectors[index])
        else:
            self.disliked_vectors.append(self.book_vectors[index])

        self.user_vector = np.zeros(self.book_vectors.shape[1])
        if len(self.liked_vectors) > 0:
            self.user_vector += np.average(self.liked_vectors, axis=0)
        if len(self.disliked_vectors) > 0:
            self.user_vector -= np.average(self.disliked_vectors, axis=0)
        
class Weighted_Rocchio(Rocchio):
    def __init__(self, book_vectors, decay: float):
        super().__init__(book_vectors)
        self.decay = decay
    
    def update(self, index: int, liked: bool):
        pass

class LinUCB():
    def __init__(self, book_vectors: np.ndarray, alpha: float = 1, seen_indices: list = []):
        _, n_features = book_vectors.shape

        self.seen_indices = seen_indices

        self.A_inv = np.eye(n_features)
        self.b = np.zeros(n_features)

        self.book_vectors = book_vectors

        self.alpha = alpha
    

    def score(self, book_index: int) -> float:
        book_x = self.book_vectors[book_index]

        theta = self.A_inv @ self.b

        expected = np.dot(theta, book_x)
        uncertainty = np.sqrt(np.transpose(book_x) @ self.A_inv @ book_x)
        result = expected + uncertainty

        # print(f"{book_index} | Expected: {expected:.2f} | Uncertainty: {uncertainty:.2f} | Total: {result:.2f}")

        return result
        
    def recommend(self, seen_indices: set):
        scores = []
        candidates = []
        for i in range(len(self.book_vectors)):
            if i in seen_indices:
                continue
            
            candidates.append(i)
            scores.append(self.score(i))

        best = np.argmax(scores)
        return candidates[best]
    
    def update(self, book_index: int, liked: bool) -> None:
        book_x = self.book_vectors[book_index]

        #update matrices
        self.A_inv -= (self.A_inv @ np.outer(book_x, book_x) @ self.A_inv) / (1 + book_x @ self.A_inv @ book_x)
        self.b += int(liked) * book_x
        

if __name__ == "__main__":
    # thriller, romance, sci-fi
    test_vectors = np.load("output/book_vectors.npy")[:500]
    with open("output/book_data.json", 'r', encoding="utf-8") as f:
        book_list= json.load(f)["data"]["books"][:500]
    

    # scaler = StandardScaler()
    # test_vectors = scaler.fit_transform(test_vectors)
    test_vectors = normalize(test_vectors, norm='l2')
    
    recommender = LinUCB(test_vectors)

    while True:
        rec = recommender.recommend()
        print(book_list[rec]["title"])
        print(book_list[rec]["genres"]["names"])
        liked = input("y/n: ") == "y"
        recommender.update(rec, liked)
    




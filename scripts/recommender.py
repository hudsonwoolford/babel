import numpy as np
import vector_utils



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

class LinUCB:
    def __init__(self, book_vectors: np.ndarray, id_2_index: dict, alpha: float = 1.0):

        self.book_vectors = book_vectors
        self.id_2_index = id_2_index
        self.index_2_id = {value: key for key, value in id_2_index.items()}
        self.A_inv = np.array([np.eye(book_vectors.shape[1]) for _ in range(len(book_vectors))])
        self.b = np.zeros(book_vectors.shape)
        self.alpha = alpha
    
    def score(self, book_id):
        index = self.id_2_index[book_id]
        x = self.book_vectors[index]

        A_inv = self.A_inv[index]

        #ridge regress
        theta = A_inv @ self.b[index]

        #exploit / explore
        exploit = theta @ x
        explore = self.alpha * np.sqrt(x @ A_inv @ x)
        return exploit + explore
        
    def recommend(self, seen_ids: set):

        scores = []
        candidate_indices = []
        for i in range(len(self.book_vectors)):
            book_id = self.index_2_id[i]
            if book_id in seen_ids:
                continue
            candidate_indices.append(i)
            scores.append(self.score(book_id))
        
        max_index = np.argmax(np.array(scores))
        return self.index_2_id[candidate_indices[max_index]]

    def update(self, book_id, liked: bool):
        book_index = self.id_2_index[book_id]
        x = self.book_vectors[book_index]
        r = int(liked)

        A_inv = self.A_inv[book_index]
        Ax = A_inv @ x
        A_inv -= np.outer(Ax, Ax) / (1 + x @ Ax)
        self.b[book_index] += r * x



import numpy as np

def cosine_similarity(vec_1: np.ndarray, vec_2: np.ndarray) -> float:
    """Calculates the cosine similarity (cos of angle between) of two vectors 

    Args:
        vec_1 (np.ndarray): vector
        vec_2 (np.ndarray): vector

    Returns:
        float: cosine value, domain: [-1, 1]
    """

    denom = np.linalg.norm(vec_1) * np.linalg.norm(vec_2)
    denom = 1 if denom == 0 else denom

    res = np.dot(vec_1, vec_2) / denom
    return res

def norm_concatenate(*args) -> np.ndarray:
    """Normalizes inputted vectors and then concatenates them

    Returns:
        np.ndarray: combined vector
    """

    #normalize each vector 
    normalized = []
    for vec in args:
        denom = np.linalg.norm(vec)
        denom = 1 if denom == 0 else denom
        normalized.append(vec / denom)

    #return concatenation
    return np.concatenate(normalized)

def list_norm_concatenate(*args) -> np.ndarray:
    """Takes lists of vectors (as ndarrays) and norm_concatenates each index

    Returns:
        np.ndarray: combined vectors
    """

    result = []
    #normalize and concatenate each vector 
    for i in range(len(args[0])):
        vecs = tuple([arg[i] for arg in args])
        result.append(norm_concatenate(*vecs))
    
    result = np.stack(result)

    #return concatenation
    return result

def arg_n_closest(vec: np.ndarray, search: np.ndarray, n: int, similarity_metric=cosine_similarity) -> np.ndarray:
    """Returns the n closest indices to the vector in the given search space

    Args:
        vec (np.ndarray): key vector
        search (np.ndarray): search space of vectors
        n (int): number of indices
        similarity_metric (_type_, optional): similarity metric function. Defaults to cosine_similarity.

    Returns:
        np.ndarray: the n closest indices
    """

    N = len(search) #size of search space
    similarities = np.zeros(N)
    for i in range(N):
        similarities[i]= similarity_metric(vec, search[i])

    ranked = np.argsort(similarities)[::-1]

    return ranked[:n]
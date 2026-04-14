import numpy as np
import json
import embedding_model
import vector_utils
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def map_vocab(vocabulary: list) -> dict:
    """Maps a vocabulary to indices, runs in order

    Args:
        vocabulary (list): all possible values / vocabulary

    Returns:
        dict: mapping
    """

    index_mapping = {}
    for i in range(len(vocabulary)):
        index_mapping[vocabulary[i]] = i

    return index_mapping

def get_all_items(books: list, extractor) -> list:
    """Gets all types/possible values of a certain item key for the books

    Args:
        books (list): list of dictionaries to represent each book
        extractor (lambda func): the lambda function to index the item

    Returns:
        list: a list of all possible values
    """

    items = set()
    for book in books:
        item = extractor(book)

        if item == None:
            continue
        elif isinstance(item, (list, tuple, set)):
            items.update(item)
        else:
            items.add(item)

    return list(items)

def binary_vec(values: list, vocabulary_map: dict) -> np.ndarray:

    vec = np.zeros(len(vocabulary_map))

    for val in values:
        index = vocabulary_map[val]
        vec[index] = 1
    
    return vec

def weighted_vec(values: list, counts: list, vocabulary_map: dict) -> np.ndarray:
    """Converts a list of values and counts to a weighted vector

    Args:
        values (list): Given values
        counts (list): Number of votes per tag
        vocabulary_map (dict): All possible values mapped to their index

    Returns:
        np.ndarray: Resulting weighted vector
    """

    vec = np.zeros(len(vocabulary_map))

    #calculate weight per value (normalized by max value)
    max_count = counts[0] if len(counts) > 0 else 1 #assuming still sorted
    max_count = 1 if max_count == 0 else 1

    weights = [c / max_count for c in counts]

    for i in range(len(values)):
        index = vocabulary_map[values[i]]

        vec[index] = weights[i]
    
    return vec

def generate_tag_vecs(book_list: list, value_extractor, count_extractor):

    tag_vocab = get_all_items(book_list, value_extractor)
    mapped_vocab = map_vocab(tag_vocab)
    res_vectors = np.zeros((len(book_list), len(tag_vocab)))

    for i in range(len(res_vectors)):
        book = book_list[i]
        values = value_extractor(book)
        counts = count_extractor(book)
        res_vectors[i] = weighted_vec(values, counts, mapped_vocab)
    
    return res_vectors

def reduce_vec_dim(vec: np.ndarray, n_dim: int):
    vec_scaled = StandardScaler().fit_transform(vec)
    pca = PCA(n_dim)
    return pca.fit_transform(vec_scaled)

def main():

    #load book data
    with open("output/book_data.json") as f:
        book_data = json.load(f)
    book_list = book_data["data"]["books"]


    # #genres
    genre_vecs = generate_tag_vecs(book_list, 
                                   lambda b: b["genres"]["names"], 
                                   lambda b: b["genres"]["counts"])
    genre_vecs = reduce_vec_dim(genre_vecs, 25)
    
    #moods
    mood_vecs = generate_tag_vecs(book_list,
                                  lambda b: b["moods"]["names"],
                                  lambda b: b["moods"]["counts"])
    mood_vecs = reduce_vec_dim(mood_vecs, 25)
    # mood_vecs = np.array([reduce_vec_dim(vec, 25) for vec in mood_vecs])
    
    #descriptions
    descriptions = []
    for book in book_list:
        desc = book.get("description", "")
        if desc == None:
            desc = ""

        descriptions.append(desc)

    embedding_model.init_model()
    desc_vecs = embedding_model.embed_texts(descriptions)
    # desc_vecs = reduce_vec_dim(desc_vecs, 50)
    # desc_vecs = np.array([reduce_vec_dim(vec, 50) for vec in desc_vecs])

    #concatenate all vectors
    final_vecs = vector_utils.list_norm_concatenate(genre_vecs, mood_vecs, desc_vecs)

    #save final
    np.save("output/book_vectors.npy", final_vecs)


if __name__ == "__main__":
    main()

    # vecs = np.load("./output/book_vectors.npy")

    # while True:
    #     index = int(input("Index: "))

    #     # print(vecs[index])
    #     closest = arg_n_closest(vecs[index], vecs, 10)
    #     print(vecs[closest[0]])
    #     # print(closest)

    #     for c in closest:
    #         print(book_list[c]["title"])
    #         print(book_list[c]["genres"]["values"])
    #         print(book_list[c]["moods"]["values"])

    
            
        


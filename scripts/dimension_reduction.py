import numpy as np
# from sklearn.preprocessing import StandardScaler  # to standardize the features
from sklearn.decomposition import PCA  # to apply PCA


def change_dimensions(vectors: np.ndarray, dimensions: int) -> np.ndarray:
    """Changes dimensions of vectors through PCA analysis

    Args:
        vectors (np.ndarray): input vectors
        dimensions (int): target dimensions

    Returns:
        np.ndarray: changed vectors
    """

    if dimensions < 1:
        print("Warning: Invalid dimension input")
        return vectors

    #PCA analysis
    pca = PCA(n_components=dimensions)
    changed_vectors = pca.fit_transform(vectors)

    # print("Variance retained:", pca.explained_variance_ratio_.sum())

    return changed_vectors
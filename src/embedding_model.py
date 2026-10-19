from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_PATH = "sentence-transformers/all-MiniLM-L6-v2"
MODEL = None

def init_model():
    global MODEL
    
    MODEL = SentenceTransformer(MODEL_PATH)

def embed_texts(texts: list) -> np.ndarray:
    """Converts texts to vectors via loaded model

    Args:
        texts (list): list of strings

    Returns:
        np._ArrayT: text vectors vectors
    """
    return MODEL.encode(texts)

if __name__ == "__main__":
    pass
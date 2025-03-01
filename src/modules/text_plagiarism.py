from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ✅ Load a multilingual Sentence Transformer model
model = SentenceTransformer('models/distiluse-base-multilingual-cased-v2')

def get_text_embedding(text):
    """Generate embedding for a given text."""
    return model.encode([text])[0]

def compute_text_similarity(text1, text2):
    """Compute cosine similarity between two texts."""
    if not text1.strip() or not text2.strip():
        return 0.0  # Return 0% similarity if either input is empty

    emb1 = get_text_embedding(text1)
    emb2 = get_text_embedding(text2)
    sim = cosine_similarity([emb1], [emb2])[0][0]
    return round(sim, 4)  # Keep only 4 decimal places

# src/modules/image_plagiarism.py
import numpy as np
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained ResNet50 model (without top layers) for feature extraction
model_img = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def get_image_embedding(img_path):
    """Extract image embedding using ResNet50."""
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    features = model_img.predict(x)
    return features.flatten()

def compute_image_similarity(img_path1, img_path2):
    """Compute cosine similarity between two images."""
    emb1 = get_image_embedding(img_path1)
    emb2 = get_image_embedding(img_path2)
    sim = cosine_similarity([emb1], [emb2])[0][0]
    return sim

# src/main.py
from modules import text_plagiarism, image_plagiarism, code_plagiarism

def demo_text():
    text1 = "This is an example of plagiarism detection in English."
    text2 = "Este es un ejemplo de detección de plagio en español."
    sim = text_plagiarism.compute_text_similarity(text1, text2)
    print("Text Similarity:", sim)

def demo_image():
    # Ensure you have two sample images in a folder named "data" (create if needed)
    sim = image_plagiarism.compute_image_similarity('data/sample_image1.jpg', 'data/sample_image2.jpg')
    print("Image Similarity:", sim)

def demo_code():
    code1 = """
def add(a, b):
    return a + b
"""
    code2 = """
def add_numbers(x, y):
    return x + y
"""
    sim = code_plagiarism.compute_code_similarity(code1, code2)
    print("Code Similarity:", sim)

if __name__ == "__main__":
    demo_text()
    demo_code()
    # Uncomment the following line when sample images are available:
    # demo_image()

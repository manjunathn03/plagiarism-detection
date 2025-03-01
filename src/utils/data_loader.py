# src/utils/data_loader.py
def load_text_file(filepath):
    """Load text content from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

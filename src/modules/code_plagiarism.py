# src/modules/code_plagiarism.py
import ast
from difflib import SequenceMatcher

def normalize_code(code_str):
    """
    Parse the code into an Abstract Syntax Tree (AST) and return a normalized string.
    This helps remove comments, whitespace, and formatting differences.
    """
    try:
        tree = ast.parse(code_str)
        normalized = ast.dump(tree)
        return normalized
    except Exception as e:
        print("Error parsing code:", e)
        return code_str

def compute_code_similarity(code1, code2):
    """Compute similarity between two source code snippets."""
    norm1 = normalize_code(code1)
    norm2 = normalize_code(code2)
    matcher = SequenceMatcher(None, norm1, norm2)
    return matcher.ratio()

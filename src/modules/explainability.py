# src/modules/explainability.py
import lime.lime_text

def explain_text_instance(text, classifier_fn, num_features=6):
    """
    Generate an explanation for a text instance using LIME.
    - text: The text to explain.
    - classifier_fn: A function that takes a list of texts and returns predictions.
    - num_features: Number of features to show in the explanation.
    """
    explainer = lime.lime_text.LimeTextExplainer(class_names=['Not Plagiarized', 'Plagiarized'])
    explanation = explainer.explain_instance(text, classifier_fn, num_features=num_features)
    # Return the explanation as a list of (feature, weight) tuples.
    return explanation.as_list()

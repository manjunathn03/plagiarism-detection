import requests

# API Key and Custom Search Engine ID
API_KEY = "AIzaSyBNjc5iqBzGURuVX-eusB-8KVc7OaRH8D0"
CSE_ID = "c760e58487fd643e5"

def google_search(query):
    """Search Google for text-based content."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
        "num": 5  # Limit results to 5
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Extract search results
    if "items" in data:
        return [(item["title"], item["link"], item["snippet"]) for item in data["items"]]
    else:
        return None

def google_image_search(image_query):
    """Search Google for web pages containing similar images."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": image_query,
        "searchType": "image",  # Tells Google to return image results
        "num": 5  # Limit to 5 results
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "items" in data:
        return [(item["title"], item["link"], item["image"]["contextLink"]) for item in data["items"]]
    else:
        return None

# Test the search functions (only runs if executed directly)
if __name__ == "__main__":
    # Test Text Plagiarism Search
    print("🔎 Testing Google Text Search...")
    text_query = "Plagiarism Detection in Machine Learning"
    text_results = google_search(text_query)

    if text_results:
        for title, link, snippet in text_results:
            print(f"{title}\n{link}\n{snippet}\n")
    else:
        print("No text results found.")

    # Test Image Plagiarism Search
    print("🖼️ Testing Google Image Search...")
    image_query = "Example Image Description"
    image_results = google_image_search(image_query)

    if image_results:
        for title, link, context in image_results:
            print(f"{title}\n{link}\nImage found on: {context}\n")
    else:
        print("No image results found.")

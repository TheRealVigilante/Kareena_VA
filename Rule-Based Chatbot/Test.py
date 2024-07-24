import requests

def url_exists(url):
    try:
        response = requests.get(url)
        # Check if status code is in the range of successful responses (200-299)
        return response.status_code // 100 == 2
    except requests.RequestException as e:
        # Handle exceptions like network problems, invalid URLs, etc.
        print(f"An error occurred: {e}")
        return False

# Example usage
url = "https://www.youtube.com"
if url_exists(url):
    print("URL exists!")
else:
    print("URL does not exist.")
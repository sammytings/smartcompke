import requests


API_KEY = "AIzaSyCAGITF6QC7fhB4icp-_tte2islGtAt-1Y"

PLACE_ID = "ChIJJePo5d8RLxgRb2Obcxgk9p0"


url = (
    "https://places.googleapis.com/v1/places/"
    f"{PLACE_ID}"
)


headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": (
        "displayName,"
        "rating,"
        "userRatingCount,"
        "reviews"
    ),
}


response = requests.get(
    url,
    headers=headers
)


print("STATUS:", response.status_code)

print(response.text)
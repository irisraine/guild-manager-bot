import requests
import os
from dotenv import load_dotenv

load_dotenv()
CONTENT_MODERATOR_API_KEY = os.environ['CONTENT_MODERATOR_API_KEY']


async def is_image_nsfw(image_url):
	url = "https://microsoft-content-moderator2.p.rapidapi.com/ProcessImage/Evaluate"
	payload = {
		"DataRepresentation": "URL",
		"Value": image_url
	}
	headers = {
		"content-type": "application/json",
		"X-RapidAPI-Key": CONTENT_MODERATOR_API_KEY,
		"X-RapidAPI-Host": "microsoft-content-moderator2.p.rapidapi.com"
	}

	response = requests.post(url, json=payload, headers=headers)

	return response.json().get('IsImageAdultClassified')

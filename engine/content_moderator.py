import requests
import os
from dotenv import load_dotenv
import logging

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
    try:
        response = requests.post(url, json=payload, headers=headers)
        logging.info(f"Изображение по адресу {image_url} проверено")
        return response.json().get('IsImageAdultClassified')
    except requests.exceptions.Timeout:
        logging.warning("Microsoft Content Moderator не отвечает. Файл не может быть проверен.")
        return None
    except (requests.RequestException, requests.HTTPError):
        logging.warning("Ошибка соединения с Microsoft Content Moderator. Файл не может быть проверен.")
        return None

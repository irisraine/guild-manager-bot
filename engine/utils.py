import os
import re
import requests
import logging


def get_cogs_list():
    cogs_list = []
    for filename in os.listdir('engine/cogs'):
        if filename.endswith('.py'):
            extension_name = filename[:-3]
            cogs_list.append(extension_name)
    return cogs_list


def load_cogs(client):
    cogs_list = get_cogs_list()
    for cog in cogs_list:
        try:
            client.load_extension(f'engine.cogs.{cog}')
            logging.info(f'Модуль {cog} успешно загружен.')
        except Exception as error:
            logging.error(f'Ошибка при попытке загрузки модуля {cog}. Дополнительная информация: {error}')


def get_attached_media(message):
    url_pattern = re.compile(r'(https?://\S+)')
    youtube_url_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')
    gif_vaults_domains = ['media1.tenor.com', 'tenor.com/view', 'giphy.com']

    attached_images_urls = []
    attached_videos_urls = []
    for attachment in message.attachments:
        if attachment.content_type:
            if attachment.content_type.startswith('image/'):
                attached_images_urls.append(attachment.url)
            elif attachment.content_type.startswith('video/'):
                attached_videos_urls.append(attachment.url)
    message_contents = message.content.split("\n")
    message_urls = [url_match.group() for item in message_contents if (url_match := url_pattern.search(item))]
    attached_videos_urls.extend(
        [url for url in message_urls if youtube_url_pattern.search(url)]
    )
    for url in message_urls:
        try:
            response = requests.get(url, timeout=5) if gif_vaults_domains[0] in url else requests.head(url, timeout=5)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type or any(domain in url for domain in gif_vaults_domains[1:]):
                    attached_images_urls.append(url)
        except requests.exceptions.RequestException:
            continue
        except Exception as error:
            logging.error(f"Неизвестная ошибка при обработке ссылки. Дополнительная информация: {error}")
    if not attached_images_urls and not attached_videos_urls:
        return None
    return {
        'images': attached_images_urls,
        'videos': attached_videos_urls
    }

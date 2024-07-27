import os
import logging


def load_cogs(client):
    for filename in os.listdir('engine/cogs'):
        if filename.endswith('.py'):
            extension = filename[:-3]
            extension_name = f'engine.cogs.{extension}'
            try:
                client.load_extension(extension_name)
                logging.info(f'Расширение {extension} успешно загружено.')
            except Exception as e:
                logging.error(f'Ошибка при попытке загрузки расширения {extension}. Дополнительная информация: {e}')

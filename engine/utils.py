from PIL import Image, ImageDraw, ImageFont
import engine.config as config
import os
import logging


def update_banner(members_count, voice_count):
    members_count, voice_count = str(members_count), str(voice_count)
    banner = Image.open(config.BANNER_IMAGE)
    counter_overlay = Image.open(config.COUNTER_OVERLAY_IMAGE)
    banner = banner.convert("RGBA")
    banner_width, banner_height = banner.size
    counter_overlay_width, counter_overlay_height = counter_overlay.size

    x_shift_overlay = banner_width - counter_overlay_width - 15
    y_shift_overlay = int(banner_height / 2)

    banner.paste(counter_overlay, (x_shift_overlay, y_shift_overlay), counter_overlay)
    banner_with_counter = banner.convert("RGB")
    draw = ImageDraw.Draw(banner_with_counter)
    font = ImageFont.truetype(config.CUSTOM_RDO_FONT, size=80)
    members_count_text_length = int(draw.textlength(members_count, font))
    voice_count_text_length = int(draw.textlength(voice_count, font))

    x_shift_text_users, y_shift_text_users = (banner_width - members_count_text_length - 30), y_shift_overlay + 5
    x_shift_text_voice, y_shift_text_voice = (banner_width - voice_count_text_length - 30), y_shift_overlay + 110

    draw.text((x_shift_text_users, y_shift_text_users), members_count, fill='white', font=font)
    draw.text((x_shift_text_voice, y_shift_text_voice), voice_count, fill='white', font=font)
    banner_with_counter.save(config.BANNER_WITH_COUNTER_IMAGE)


def get_banner_binary_data(image):
    with open(image, 'rb') as banner_file:
        banner_binary_data = banner_file.read()
    return banner_binary_data


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

from PIL import Image, ImageDraw, ImageFont
import engine.config as config


def update_banner(members_count, voice_count):
    members_count, voice_count = str(members_count), str(voice_count)
    banner = Image.open(config.BANNER_IMAGE_COUNTER_BLANK)
    draw = ImageDraw.Draw(banner)
    font = ImageFont.truetype(config.CUSTOM_RDO_FONT, size=70)
    members_count_text_length = int(draw.textlength(members_count, font))
    voice_count_text_length = int(draw.textlength(voice_count, font))

    draw.text((770 - members_count_text_length, 275), members_count, fill='white', font=font)
    draw.text((770 - voice_count_text_length, 365), voice_count, fill='white', font=font)
    banner.save(config.BANNER_IMAGE_COUNTER)


def get_banner_binary_data(image):
    with open(image, 'rb') as banner_file:
        banner_binary_data = banner_file.read()
    return banner_binary_data

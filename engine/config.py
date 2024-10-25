import os
from dotenv import load_dotenv


load_dotenv()

LOGGING_SETTINGS = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '[%(levelname)s][%(asctime)s] : %(message)s',
                'datefmt': '%d-%m-%Y %H:%M:%S'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'INFO',
            },
        }
    }

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_ID = int(os.environ['GUILD_ID'])
MEDIA_ONLY_CHANNELS = list(map(int, os.environ['MEDIA_ONLY_CHANNELS'].split(","))) if os.environ['MEDIA_ONLY_CHANNELS'] else []
ANNOUNCEMENT_CHANNELS = list(map(int, os.environ['ANNOUNCEMENT_CHANNELS'].split(","))) if os.environ['ANNOUNCEMENT_CHANNELS'] else []
COMMON_DISCUSSION_CHANNEL = int(os.environ['COMMON_DISCUSSION_CHANNEL'])
ADMIN_ROLE = int(os.environ['ADMIN_ROLE'])
MODERATOR_ROLE = int(os.environ['MODERATOR_ROLE'])
GROUP_ROLES = list(map(int, os.environ['GROUP_ROLES'].split(",")))
GROUP_LEADERS_ROLES = list(map(int, os.environ['GROUP_LEADERS_ROLES'].split(",")))
SOLO_SESSION_ROLE = int(os.environ['SOLO_SESSION_ROLE'])
SOLO_SESSION_CHANNEL = int(os.environ['SOLO_SESSION_CHANNEL'])
SOLO_SESSION_ROLE_SECOND = int(os.environ['SOLO_SESSION_ROLE_SECOND'])
SOLO_SESSION_CHANNEL_SECOND = int(os.environ['SOLO_SESSION_CHANNEL_SECOND'])
SOLO_EVENT_ROLE = int(os.environ['SOLO_EVENT_ROLE'])
SOLO_EVENT_CHANNEL = int(os.environ['SOLO_EVENT_CHANNEL'])
COMMANDS_ONLY_CHANNELS = list(map(int, os.environ['COMMANDS_ONLY_CHANNELS'].split(","))) if os.environ['COMMANDS_ONLY_CHANNELS'] else []

CONTENT_MODERATOR = {
    "api_key": os.environ['CONTENT_MODERATOR_API_KEY'],
    "url": "https://nsfw-images-detection-and-classification.p.rapidapi.com/adult-content",
    "host": "nsfw-images-detection-and-classification.p.rapidapi.com",
    "nsfw_key": "unsafe"
}

TIMEOUT_DURATION = 9000
GIF_COOLDOWN_DURATION = 600
MAX_IMAGES = 7
TIME_LIMIT = 60

BANNER_IMAGE = 'assets/banner.jpg'
BANNER_WITH_COUNTER_IMAGE = 'assets/banner_with_counter.jpg'
COUNTER_OVERLAY_IMAGE = 'assets/counter_overlay.png'
CUSTOM_RDO_FONT = 'assets/chineserocksboldcyrillic.otf'
SEPARATOR = 'assets/separator.png'

SOLO_SESSION_IMAGE = 'assets/artur-morgan-solo.gif'
BAND_IMAGE = 'assets/band.jpg'
SOLO_EVENT_IMAGE = 'assets/event.jpg'

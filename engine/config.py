import os
from dotenv import load_dotenv
import engine.utils as utils


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

CATEGORY_EMOJI = {
    "auto_threading": "🗂️",
    "authorize_band": "<:1bi:1132997100687339621>",
    "media_only": "🏞️",
    "commands_only": "⚙️",
    "no_moderation": "⛔",
    "bots_allowed": "🤖",
    "announcement": "📰",
}

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_ID = int(os.environ['GUILD_ID'])
ADMIN_ROLE = int(os.environ['ADMIN_ROLE'])
MODERATOR_ROLE = int(os.environ['MODERATOR_ROLE'])
MODERATOR_ASSISTANT_ROLE = int(os.environ['MODERATOR_ASSISTANT_ROLE'])
COMMON_DISCUSSION_CHANNEL = int(os.environ['COMMON_DISCUSSION_CHANNEL'])
SOLO_SESSION = {
    "city": {
        'role': list(map(int, os.environ['SOLO_SESSION_ROLES'].split(",")))[0],
        'channel': list(map(int, os.environ['SOLO_SESSION_CHANNELS'].split(",")))[0],
        'name': "город Подфайловск"
    },
    "suburb": {
        'role': list(map(int, os.environ['SOLO_SESSION_ROLES'].split(",")))[1],
        'channel': list(map(int, os.environ['SOLO_SESSION_CHANNELS'].split(",")))[1],
        'name': "пригород Подфайловска"
    }
}
SOLO_EVENT = {
    'role': int(os.environ['SOLO_EVENT_ROLE']),
    'channel': int(os.environ['SOLO_EVENT_CHANNEL'])
}

AUTO_THREADING_CHANNELS_JSON = "settings/auto_threading.json"
AUTO_THREADING_CHANNELS = utils.json_safeload(AUTO_THREADING_CHANNELS_JSON)['channels']
MEDIA_ONLY_CHANNELS_JSON = "settings/media_only.json"
MEDIA_ONLY_CHANNELS = utils.json_safeload(MEDIA_ONLY_CHANNELS_JSON)['channels']
COMMANDS_ONLY_CHANNELS_JSON = "settings/commands_only.json"
COMMANDS_ONLY_CHANNELS = utils.json_safeload(COMMANDS_ONLY_CHANNELS_JSON)['channels']
NO_MODERATION_CHANNELS_JSON = "settings/no_moderation.json"
NO_MODERATION_CHANNELS = utils.json_safeload(NO_MODERATION_CHANNELS_JSON)['channels']
BOTS_ALLOWED_CHANNELS_JSON = "settings/bots_allowed.json"
BOTS_ALLOWED_CHANNELS = utils.json_safeload(BOTS_ALLOWED_CHANNELS_JSON)['channels']
AUTHORIZED_BANDS_JSON = "settings/authorized_bands.json"
AUTHORIZED_BAND_ROLES = utils.json_safeload(AUTHORIZED_BANDS_JSON)['band_roles']
AUTHORIZED_BAND_LEADERS_ROLES = utils.json_safeload(AUTHORIZED_BANDS_JSON)['band_leader_roles']
ANNOUNCEMENT_CHANNELS_JSON = "settings/announcement.json"
ANNOUNCEMENT_CHANNELS = utils.json_safeload(ANNOUNCEMENT_CHANNELS_JSON)['channels']

SPECIAL_CHANNELS_CATEGORIES = {
    'auto_threading': {'ids': AUTO_THREADING_CHANNELS, 'json_file': AUTO_THREADING_CHANNELS_JSON},
    'media_only': {'ids': MEDIA_ONLY_CHANNELS, 'json_file': MEDIA_ONLY_CHANNELS_JSON},
    'commands_only': {'ids': COMMANDS_ONLY_CHANNELS, 'json_file': COMMANDS_ONLY_CHANNELS_JSON},
    'no_moderation': {'ids': NO_MODERATION_CHANNELS, 'json_file': NO_MODERATION_CHANNELS_JSON},
    'bots_allowed': {'ids': BOTS_ALLOWED_CHANNELS, 'json_file': BOTS_ALLOWED_CHANNELS_JSON},
    'announcement': {'ids': ANNOUNCEMENT_CHANNELS, 'json_file': ANNOUNCEMENT_CHANNELS_JSON},
}

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
SOLO_SESSION_LEFT_OFF_IMAGE = 'assets/solo_left_off.jpg'
BAND_IMAGE = 'assets/band.jpg'
BAND_LEFT_OFF_IMAGE = 'assets/band_left_off.jpg'
SOLO_EVENT_IMAGE = 'assets/event.jpg'
SOLO_EVENT_LEFT_OFF_IMAGE = 'assets/event_left_off.jpg'

SETTINGS_MENU_IMAGE = 'assets/settings_menu.jpg'
SUCCESS_IMAGE = 'assets/success.jpg'
ERROR_IMAGE = 'assets/error.jpg'
AUTO_THREADING_IMAGE = 'assets/auto_threading.jpg'
BAND_AUTHORIZATION_IMAGE = 'assets/band_authorization.jpg'
MEDIA_ONLY_IMAGE = 'assets/media_only.jpg'
COMMANDS_ONLY_IMAGE = 'assets/commands_only.jpg'
NO_MODERATION_IMAGE = 'assets/no_moderation.jpg'
BOTS_ALLOWED_IMAGE = 'assets/bots_allowed.jpg'
ANNOUNCEMENT_IMAGE = 'assets/announcement.jpg'

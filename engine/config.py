import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
ALLOWED_CHANNELS = list(map(int, os.environ['ALLOWED_CHANNELS'].split(","))) if os.environ['ALLOWED_CHANNELS'] else []
ANNOUNCEMENT_CHANNELS = list(map(int, os.environ['ANNOUNCEMENT_CHANNELS'].split(","))) if os.environ['ANNOUNCEMENT_CHANNELS'] else []
GUILD_ID = int(os.environ['GUILD_ID'])
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

CONTENT_MODERATOR_API_KEY = os.environ['CONTENT_MODERATOR_API_KEY']

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

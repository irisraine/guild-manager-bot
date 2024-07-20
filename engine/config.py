import os
from dotenv import load_dotenv

load_dotenv()

ALLOWED_CHANNELS = list(map(int, os.environ['ALLOWED_CHANNELS'].split(",")))
GUILD_ID = int(os.environ['GUILD_ID'])
COMMON_DISCUSSION_CHANNEL = int(os.environ['COMMON_DISCUSSION_CHANNEL'])
MODERATOR_ROLE_ID = int(os.environ['MODERATOR_ROLE_ID'])
GROUP_LEADERS_ROLES = list(map(int, os.environ['GROUP_LEADERS_ROLES'].split(",")))
SOLO_SESSION_ROLE = int(os.environ['SOLO_SESSION_ROLE'])

TIMEOUT_DURATION = 9000
GIF_COOLDOWN_DURATION = 600
MAX_IMAGES = 7
TIME_LIMIT = 60

BANNER_IMAGE = 'assets/banner.jpg'
BANNER_WITH_COUNTER_IMAGE = 'assets/banner_with_counter.jpg'
COUNTER_OVERLAY_IMAGE = 'assets/counter_overlay.png'
CUSTOM_RDO_FONT = 'assets/chineserocksboldcyrillic.otf'

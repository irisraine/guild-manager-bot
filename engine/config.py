import os
from dotenv import load_dotenv

load_dotenv()

ALLOWED_CHANNELS = list(map(int, os.environ['ALLOWED_CHANNELS'].split(",")))
GUILD_ID = int(os.environ['GUILD_ID'])
COMMON_DISCUSSION_CHANNEL = int(os.environ['COMMON_DISCUSSION_CHANNEL'])
ADMIN_ROLE = int(os.environ['ADMIN_ROLE'])
MODERATOR_ROLE = int(os.environ['MODERATOR_ROLE'])
GROUP_ROLES = list(map(int, os.environ['GROUP_ROLES'].split(",")))
GROUP_LEADERS_ROLES = list(map(int, os.environ['GROUP_LEADERS_ROLES'].split(",")))
SOLO_SESSION_ROLE = int(os.environ['SOLO_SESSION_ROLE'])
SOLO_SESSION_CHANNEL = int(os.environ['SOLO_SESSION_CHANNEL'])

TIMEOUT_DURATION = 9000
GIF_COOLDOWN_DURATION = 600
MAX_IMAGES = 7
TIME_LIMIT = 60

BANNER_IMAGE = 'assets/banner.jpg'
BANNER_WITH_COUNTER_IMAGE = 'assets/banner_with_counter.jpg'
COUNTER_OVERLAY_IMAGE = 'assets/counter_overlay.png'
CUSTOM_RDO_FONT = 'assets/chineserocksboldcyrillic.otf'

SOLO_SESSION_IMAGE = 'assets/artur-morgan-solo.gif'

from collections import deque
from datetime import datetime, timedelta
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import requests
import os
import re
from engine.nsfw_checker import is_image_nsfw

load_dotenv()
ALLOWED_CHANNELS = os.environ['ALLOWED_CHANNELS']

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

COMMENTS_THREAD_NAME = "💬 Оставить комментарии"
GREETING_BOT_MESSAGE = "Создана ветка обсуждения"
MUTE_HEADER_MESSAGE = '❌ Здравствуйте, вам бан! ❌'
MUTE_REASON_SPAM = "спамил картинками"
MUTE_REASON_NSFW = "постил непотребства"
MUTE_DESCRIPTION_MESSAGE = 'Теперь он улетает в мут, хорошенько подумать о своем поведении!'
TIMEOUT_DURATION = 9000
MAX_IMAGES = 10
TIME_LIMIT = 60

current_time = 0

user_message_statistics = {}
active_timeout = {}


async def has_attached_image(message):
    if message.attachments:
        attachment = message.attachments[0]
        return attachment.content_type.startswith('image/')


async def get_image_links(message):
    url_pattern = re.compile(r'(http|https)://\S+')
    message_content_as_list = message.content.split("\n")
    urls = list(filter(lambda item: url_pattern.match(item), message_content_as_list))
    image_urls = []
    for url in urls:
        try:
            response = requests.head(url)
            if response.status_code == 200 and 'image' in response.headers.get('content-type'):
                image_urls.append(url)
        except requests.exceptions.RequestException:
            continue
    return image_urls if image_urls else []


async def mute_user(message, reason):
    try:
        await message.author.timeout(timedelta(
            seconds=TIMEOUT_DURATION),
            reason=reason
        )
        print(f'User {message.author} has been muted.')
    except nextcord.errors.Forbidden:
        print(f'Privileged users cannot be blocked by this bot!')


@client.event
async def on_message(message):
    if message.author.bot:
        return

    message_has_attached_images = await has_attached_image(message)
    message_image_links = await get_image_links(message)

    is_nsfw = False

    if message_has_attached_images or message_image_links:
        user_id = message.author.id

        if user_id not in user_message_statistics:
            user_message_statistics[user_id] = deque(maxlen=MAX_IMAGES)
        user_message_statistics[user_id].append(message.created_at.timestamp())

        if user_id in user_message_statistics and len(user_message_statistics[user_id]) == MAX_IMAGES:
            oldest_message_time = user_message_statistics[user_id].popleft()
            global current_time
            current_time = message.created_at.timestamp()
            if current_time - oldest_message_time <= TIME_LIMIT:
                active_timeout[user_id] = {'channel': message.channel.id,
                                            'reason': MUTE_REASON_SPAM
                                           }
                await mute_user(message, MUTE_REASON_SPAM)
                user_message_statistics.pop(user_id, None)
                return

        message_attachment_images_url = [attachment.url for attachment in message.attachments]
        message_all_images_urls = message_attachment_images_url + message_image_links

        for image_url in message_all_images_urls:
            if await is_image_nsfw(image_url):
                is_nsfw = True
                active_timeout[user_id] = {'channel': message.channel.id,
                                            'reason': MUTE_REASON_NSFW
                                           }
                await mute_user(message, MUTE_REASON_NSFW)
                try:
                    await message.delete()
                except nextcord.errors.NotFound:
                    print(f'Message not found or already deleted')

                break

        thread_create_permission = True
        if ALLOWED_CHANNELS:
            if str(message.channel.id) not in ALLOWED_CHANNELS:
                thread_create_permission = False

        if thread_create_permission and not is_nsfw:
            try:
                thread = await message.create_thread(
                    name=COMMENTS_THREAD_NAME,
                    auto_archive_duration=60
                )
                await thread.send(GREETING_BOT_MESSAGE)
            except nextcord.errors.HTTPException as e:
                print(f'An error occurred while creating a thread: {e}')
            except Exception as e:
                print(f'An unexpected error occurred: {e}')

    await client.process_commands(message)


@client.event
async def on_member_update(before, after):
    if not before.communication_disabled_until and after.communication_disabled_until:
        if after.id in active_timeout.keys():
            channel_id = active_timeout[after.id]['channel']
            channel = client.get_channel(channel_id)
            reason_for_muting = active_timeout[after.id]['reason']

            ban_info = nextcord.Embed(
                title=MUTE_HEADER_MESSAGE,
                description=f'Абоба {after.mention} {reason_for_muting}. {MUTE_DESCRIPTION_MESSAGE}',
                colour=nextcord.Colour.from_rgb(255, 0, 0)
            )
            await channel.send(embed=ban_info)
            del active_timeout[after.id]

            if reason_for_muting == MUTE_REASON_SPAM:
                spam_starting_time = datetime.fromtimestamp(current_time - TIME_LIMIT)
                async for message in channel.history(limit=100, after=spam_starting_time):
                    if message.author == after:
                        try:
                            await message.delete()
                        except nextcord.errors.NotFound:
                            print(f'Message not found or already deleted')


@client.event
async def on_ready():
    print(f'Logged in as: {client.user.name}')

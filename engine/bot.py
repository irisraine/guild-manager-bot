from collections import deque
from datetime import datetime, timedelta
import nextcord
from nextcord.ext import commands, tasks
import requests
import re
import os
import logging
from dotenv import load_dotenv
from engine.content_moderator import is_image_nsfw
import engine.utils as utils
import engine.config as config

load_dotenv()
intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents)

ALLOWED_CHANNELS = os.environ['ALLOWED_CHANNELS']
GUILD_ID = int(os.environ['GUILD_ID'])

COMMENTS_THREAD_NAME = "💬 Оставить комментарии"
GREETING_BOT_MESSAGE = "Создана ветка обсуждения"
MUTE_HEADER_MESSAGE = '❌ Здравствуйте, вам бан! ❌'
MUTE_REASONS = {'SPAM': "спамил картинками",
                'NSFW': "постил непотребства"}
MUTE_DESCRIPTION_MESSAGE = 'Теперь он улетает в мут, хорошенько подумать о своем поведении!'

user_message_statistics = {}
muted_users = {}

members_count = 0
voice_count = 0


def get_attached_images_urls(message):
    attached_images_urls = []
    for attachment in message.attachments:
        if attachment.content_type and attachment.content_type.startswith('image/'):
            attached_images_urls.append(attachment.url)
    return attached_images_urls


def get_textarea_images_urls(message):
    url_pattern = re.compile(r'(http|https)://\S+')
    message_content_as_list = message.content.split("\n")
    urls = [url_match.group() for url_match
            in list(map(lambda item: url_pattern.search(item), message_content_as_list))
            if url_match]
    textarea_urls = []
    for url in urls:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200 and 'image' in response.headers.get('content-type'):
                textarea_urls.append(url)
        except requests.exceptions.RequestException:
            continue
    return textarea_urls


async def mute_user(message, reason):
    try:
        await message.author.timeout(timedelta(
            seconds=config.TIMEOUT_DURATION),
            reason=reason
        )
        logging.info(f"Пользователь {message.author} отправлен в мут.")
    except nextcord.errors.Forbidden:
        logging.info(f"Бот не может отправлять в мут привилегированных пользователей.")


async def delete_message(message):
    try:
        await message.delete()
    except nextcord.errors.NotFound:
        logging.warning("Сообщение не найдено, либо оно уже было удалено ранее.")


async def create_thread(message):
    try:
        thread = await message.create_thread(
            name=COMMENTS_THREAD_NAME,
            auto_archive_duration=60
        )
        await thread.send(GREETING_BOT_MESSAGE)
    except nextcord.errors.HTTPException as e:
        logging.error(f"При попытке создания треда возникла следующая ошибка: {e}.")
    except Exception as e:
        logging.error(f"При попытке создания треда возникла неопределенная ошибка: {e}.")


async def check_spam(message):
    user_id = message.author.id
    global user_message_statistics
    global muted_users
    if user_id not in user_message_statistics:
        user_message_statistics[user_id] = deque(maxlen=config.MAX_IMAGES)
    user_message_statistics[user_id].append(message.created_at.timestamp())
    if user_id in user_message_statistics and len(user_message_statistics[user_id]) == config.MAX_IMAGES:
        oldest_message_time = user_message_statistics[user_id].popleft()
        current_time = message.created_at.timestamp()
        if current_time - oldest_message_time <= config.TIME_LIMIT:
            muted_users[user_id] = {'channel': message.channel,
                                    'reason': MUTE_REASONS['SPAM']}
            await mute_user(message, MUTE_REASONS['SPAM'])
            spam_initial_time = datetime.fromtimestamp(current_time - config.TIME_LIMIT)
            async for item in message.channel.history(limit=None, after=spam_initial_time):
                if item.author == message.author:
                    await delete_message(item)
            user_message_statistics.pop(user_id, None)
            return True


async def check_nsfw(message, message_images_urls):
    user_id = message.author.id
    global muted_users
    for image_url in message_images_urls:
        if await is_image_nsfw(image_url):
            muted_users[user_id] = {'channel': message.channel,
                                    'reason': MUTE_REASONS['NSFW']}
            await mute_user(message, MUTE_REASONS['NSFW'])
            await delete_message(message)
            logging.info(f"Изображение по адресу {image_url} содержит NSFW-контент и было удалено.")
            return True


@client.event
async def on_message(message):
    if message.author.bot:
        return

    message_images_urls = get_textarea_images_urls(message) + get_attached_images_urls(message)
    if message_images_urls:
        if not message.author.guild_permissions.administrator:
            is_spam = await check_spam(message)
            is_nsfw = await check_nsfw(message, message_images_urls)
            if is_spam or is_nsfw:
                return
        if ALLOWED_CHANNELS and str(message.channel.id) not in ALLOWED_CHANNELS:
            return
        logging.info(f"Создан тред для изображения {message_images_urls[0]}")
        await create_thread(message)

    await client.process_commands(message)


@client.event
async def on_member_update(before, after):
    global muted_users
    if not before.communication_disabled_until and after.communication_disabled_until:
        if after.id in muted_users.keys():
            channel = muted_users[after.id]['channel']
            reason_for_muting = muted_users[after.id]['reason']
            mute_info = nextcord.Embed(
                title=MUTE_HEADER_MESSAGE,
                description=f'Абоба {after.mention} {reason_for_muting}. {MUTE_DESCRIPTION_MESSAGE}',
                colour=nextcord.Colour.from_rgb(255, 0, 0)
            )
            await channel.send(embed=mute_info)
            muted_users.pop(after.id, None)


@tasks.loop(minutes=10)
async def banner_member_counter():
    guild = client.get_guild(GUILD_ID)
    global members_count, voice_count
    current_members_count = guild.member_count
    current_voice_count = sum(1 for member in guild.members if member.voice)

    if current_members_count != members_count or current_voice_count != voice_count:
        utils.update_banner(
            members_count=current_members_count,
            voice_count=current_voice_count
        )
        banner_binary_data = utils.get_banner_binary_data(config.BANNER_IMAGE_COUNTER)
        await guild.edit(banner=banner_binary_data)
        members_count, voice_count = current_members_count, current_voice_count


@client.command()
@commands.has_permissions(administrator=True)
async def static_banner(ctx):
    guild = client.get_guild(GUILD_ID)
    banner_member_counter.stop()
    banner_binary_data = utils.get_banner_binary_data(config.BANNER_IMAGE)
    await guild.edit(banner=banner_binary_data)
    logging.info(f'Динамический баннер отключен.')


@client.command()
@commands.has_permissions(administrator=True)
async def dynamic_banner(ctx):
    banner_member_counter.start()
    logging.info(f'Динамический баннер активирован.')


@static_banner.error
@dynamic_banner.error
async def permission_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            embed=nextcord.Embed(
                title="Ошибка",
                description="Эта команда доступна только администраторам.",
                colour=nextcord.Colour.from_rgb(255, 0, 0))
        )


@client.event
async def on_ready():
    logging.info(f'Бот залогинен под именем: {client.user.name}')

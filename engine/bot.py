from collections import deque
from datetime import datetime, timedelta
import nextcord
from nextcord.ext import commands, tasks, application_checks
import requests
import re
import logging
from engine.content_moderator import is_image_nsfw
import engine.config as config

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='&', intents=intents, default_guild_ids=[config.GUILD_ID])

COMMENTS_THREAD_NAME = "💬 Оставить комментарии"
GREETING_BOT_MESSAGE = "Создана ветка обсуждения"
MUTE_HEADER_MESSAGE = '❌ Здравствуйте, вам бан! ❌'
GIF_WARNING_HEADER_MESSAGE = '💢 It\'s time to stop! 💢'
ERROR_HEADER = "Ошибка"
ERROR_MESSAGE = "У вас недостаточно прав для использования данной команды!"
MUTE_REASONS = {'SPAM': "спамил картинками",
                'NSFW': "постил непотребства"}
MUTE_DESCRIPTION_MESSAGE = "Теперь он улетает в мут, хорошенько подумать о своем поведении!"
GIF_WARNING_DESCRIPTION_MESSAGE = ("Ваш бесплатный пробный период использования гифок на данный момент закончился. "
                                   "Для продления насыпьте костей или сена в кормушку модераторам.")

unwanted_content = False
user_message_statistics = {}
muted_users = {}

is_gif_limits = False
users_gifs = {}


def get_attached_media(message):
    url_pattern = re.compile(r'(https?://\S+)')
    youtube_url_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')
    gif_vaults_domains = ['media1.tenor.com', 'tenor.com/view', 'giphy.com']

    attached_images_urls = []
    attached_videos_urls = []
    for attachment in message.attachments:
        if attachment.content_type:
            if attachment.content_type.startswith('image/'):
                attached_images_urls.append(attachment.url)
            elif attachment.content_type.startswith('video/'):
                attached_videos_urls.append(attachment.url)
    message_contents = message.content.split("\n")
    message_urls = [url_match.group() for item in message_contents if (url_match := url_pattern.search(item))]
    attached_videos_urls.extend(
        [url for url in message_urls if youtube_url_pattern.search(url)]
    )
    for url in message_urls:
        try:
            response = requests.get(url, timeout=5) if gif_vaults_domains[0] in url else requests.head(url, timeout=5)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type or any(domain in url for domain in gif_vaults_domains[1:]):
                    attached_images_urls.append(url)
        except requests.exceptions.RequestException:
            continue
        except Exception as error:
            logging.error(f"Неизвестная ошибка при обработке ссылки. Дополнительная информация: {error}")
    return {
        'images': attached_images_urls,
        'videos': attached_videos_urls
    }


async def mute_user(message, reason):
    try:
        await message.author.timeout(
            timedelta(seconds=config.TIMEOUT_DURATION),
            reason=reason
        )
        logging.info(f"Пользователь {message.author} отправлен в мут.")
    except nextcord.errors.Forbidden:
        logging.info("Бот не может отправлять в мут привилегированных пользователей.")


async def delete_message(message):
    try:
        await message.delete()
    except nextcord.errors.NotFound:
        logging.warning("Сообщение не найдено, либо оно уже было удалено ранее.")
    except Exception as error:
        logging.error(f"При попытке удаления сообщения возникла непредвиденная ошибка: {error}.")


async def safe_fetch_message(message_id):
    channel = client.get_channel(config.COMMON_DISCUSSION_CHANNEL)
    try:
        fetched_message = await channel.fetch_message(message_id)
        return fetched_message
    except nextcord.NotFound:
        logging.info("Сообщение с предупреждением отсутствует, видимо, оно было ранее удалено вручную.")
    except Exception as error:
        logging.error(f"При попытке получения сообщения возникла непредвиденная ошибка: {error}.")


async def create_thread(message):
    if config.ALLOWED_CHANNELS and message.channel.id not in config.ALLOWED_CHANNELS:
        return
    try:
        thread = await message.create_thread(
            name=COMMENTS_THREAD_NAME,
            auto_archive_duration=60
        )
        await thread.send(GREETING_BOT_MESSAGE)
        logging.info(f"Создан тред для сообщения id:{message.id}, содержащим медиаконтент")
    except nextcord.errors.HTTPException as error:
        logging.error(f"При попытке создания треда возникла ошибка сетевого соединения: {error}.")
    except Exception as error:
        logging.error(f"При попытке создания треда возникла непредвиденная ошибка: {error}.")


async def check_spam(message):
    user_id = message.author.id
    global unwanted_content
    global user_message_statistics
    global muted_users
    if user_id not in user_message_statistics:
        user_message_statistics[user_id] = deque(maxlen=config.MAX_IMAGES)
    user_message_statistics[user_id].append(message.created_at.timestamp())
    if user_id in user_message_statistics and len(user_message_statistics[user_id]) == config.MAX_IMAGES:
        oldest_message_time = user_message_statistics[user_id].popleft()
        current_time = message.created_at.timestamp()
        if current_time - oldest_message_time <= config.TIME_LIMIT:
            unwanted_content = True
            muted_users[user_id] = {'channel': message.channel,
                                    'reason': MUTE_REASONS['SPAM']}
            await mute_user(message, MUTE_REASONS['SPAM'])
            spam_initial_time = datetime.fromtimestamp(current_time - config.TIME_LIMIT)
            async for item in message.channel.history(limit=None, after=spam_initial_time):
                if item.author == message.author:
                    await delete_message(item)
            user_message_statistics.pop(user_id, None)


async def check_nsfw(message, message_images_urls):
    user_id = message.author.id
    global unwanted_content
    global muted_users
    for image_url in message_images_urls:
        if await is_image_nsfw(image_url):
            unwanted_content = True
            muted_users[user_id] = {'channel': message.channel,
                                    'reason': MUTE_REASONS['NSFW']}
            await mute_user(message, MUTE_REASONS['NSFW'])
            await delete_message(message)
            logging.info(f"Изображение по адресу {image_url} содержит NSFW-контент и было удалено.")


async def check_gifs(message, message_images_urls):
    gif_extension_pattern = re.compile(r"tenor\.com|giphy\.com|\.gif($|\?|&)")
    if any(gif_extension_pattern.search(image_url) for image_url in message_images_urls):
        global users_gifs
        user_id = message.author.id
        current_time = datetime.now()
        cooldown = timedelta(seconds=config.GIF_COOLDOWN_DURATION)
        if user_id in users_gifs and current_time - users_gifs[user_id].get('time') < cooldown:
            if users_gifs[user_id].get('warning_id'):
                previous_warning_id = users_gifs[user_id].get('warning_id')
                previous_warning_message = await safe_fetch_message(previous_warning_id)
                if previous_warning_message:
                    await delete_message(previous_warning_message)
            warning_message = await message.channel.send(embed=nextcord.Embed(
                title=GIF_WARNING_HEADER_MESSAGE,
                description=f"Уважаемый {message.author.mention}! {GIF_WARNING_DESCRIPTION_MESSAGE}",
                colour=nextcord.Color.red())
            )
            users_gifs[user_id]['warning_id'] = warning_message.id
            await delete_message(message)
        else:
            users_gifs[user_id] = {'time': current_time, 'warning_id': None}


@client.event
async def on_message(message):
    if message.author.bot:
        return

    message_media_urls = get_attached_media(message)
    if message_media_urls['images']:
        if not message.author.guild_permissions.administrator:
            await check_spam(message)
            await check_nsfw(message, message_media_urls['images'])
            if unwanted_content:
                return
            if is_gif_limits and message.channel.id == config.COMMON_DISCUSSION_CHANNEL:
                await check_gifs(message, message_media_urls['images'])
    if message_media_urls['images'] or message_media_urls['videos']:
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
                colour=nextcord.Color.red()
            )
            await channel.send(embed=mute_info)
            muted_users.pop(after.id, None)


@tasks.loop(minutes=10)
async def purge_gif_warnings():
    for user_id, gif_info in users_gifs.items():
        current_warning_id = gif_info.get('warning_id')
        if current_warning_id:
            current_warning_message = await safe_fetch_message(current_warning_id)
            if current_warning_message:
                await delete_message(current_warning_message)
                users_gifs[user_id]['warning_id'] = None


@client.slash_command(description="Ограничения на использование гифок")
@application_checks.has_role(config.ADMIN_ROLE)
async def gif_limits(
        interaction: nextcord.Interaction,
        toggle: str = nextcord.SlashOption(
            description="Статус ограничений",
            choices={"установить": "on", "отменить": "off"}
        )):
    global is_gif_limits
    if toggle == "on":
        is_gif_limits = True
        if not purge_gif_warnings.is_running():
            purge_gif_warnings.start()
    elif toggle == "off":
        is_gif_limits = False
        purge_gif_warnings.stop()
        users_gifs.clear()
    status = "установлено" if toggle == "on" else "отменено"
    await interaction.response.send_message(
        embed=nextcord.Embed(
            description=f"Ограничение на использование гифок {status}.",
            colour=nextcord.Color.red())
    )
    logging.info(f'Ограничение на использование гифок {status}.')


@client.slash_command(description="Загрузить или выгрузить расширение")
@application_checks.has_role(config.ADMIN_ROLE)
async def toggle_extension(interaction: nextcord.Interaction, extension: str):
    extension_name = f'engine.cogs.{extension}'
    try:
        if extension_name in client.extensions:
            client.unload_extension(extension_name)
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    description=f"Расширение {extension} отключено.",
                    colour=nextcord.Color.green()))
            logging.info(f'Расширение {extension} отключено.')
        else:
            client.load_extension(extension_name)
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    description=f"Расширение {extension} успешно активировано.",
                    colour=nextcord.Color.green()))
            logging.info(f'Расширение {extension} успешно активировано.')
    except Exception as error:
        await interaction.response.send_message(
            embed=nextcord.Embed(
                description=f"Ошибка при попытке загрузки расширения {extension}.",
                colour=nextcord.Color.red()))
        logging.error(f'Ошибка при попытке загрузки расширения {extension}. Дополнительная информация: {error}')


@client.event
async def on_application_command_error(interaction: nextcord.Interaction, error):
    handled_errors = (application_checks.ApplicationMissingAnyRole, application_checks.ApplicationMissingRole)
    if isinstance(error, handled_errors):
        await interaction.response.send_message(
            embed=nextcord.Embed(
                title=ERROR_HEADER,
                description=ERROR_MESSAGE,
                colour=nextcord.Color.red()), ephemeral=True
        )
    else:
        logging.error(f"При использовании команды произошла непредвиденная ошибка: {error}")


@client.event
async def on_ready():
    logging.info(f'Бот залогинен под именем: {client.user.name}')

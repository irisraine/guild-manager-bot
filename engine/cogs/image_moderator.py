import nextcord
from nextcord.ext import commands, tasks, application_checks
import logging
import requests
import re
from datetime import datetime, timedelta
from collections import deque
import engine.config as config
import engine.messages as messages

MUTE_REASONS = {'SPAM': "спамил картинками", 'NSFW': "постил непотребства"}


class ImageModerator(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.user_message_statistics = {}
        self.muted_users = {}
        self.is_gif_limits = False
        self.users_gifs = {}

    @staticmethod
    async def is_image_nsfw(image_url):
        url = config.CONTENT_MODERATOR["url"]
        payload = {"url": image_url}
        headers = {
            "content-type": "application/json",
            "x-rapidapi-key": config.CONTENT_MODERATOR["api_key"],
            "x-rapidapi-host": config.CONTENT_MODERATOR["host"],
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            logging.info(f"Изображение по адресу {image_url} проверено")
            return response.json().get(config.CONTENT_MODERATOR["nsfw_key"])
        except requests.exceptions.Timeout:
            logging.warning("Сервис анализа изображений не отвечает. Файл не может быть проверен.")
        except (requests.RequestException, requests.HTTPError):
            logging.warning("Ошибка соединения с сервисом анализа изображений. Файл не может быть проверен.")

    @staticmethod
    async def mute_user(message, reason):
        try:
            await message.author.timeout(
                timedelta(seconds=config.TIMEOUT_DURATION),
                reason=reason
            )
            logging.info(f"Пользователь {message.author} отправлен в мут.")
        except nextcord.errors.Forbidden:
            logging.info("Бот не может отправлять в мут привилегированных пользователей.")

    @staticmethod
    async def delete_message(message):
        try:
            await message.delete()
        except nextcord.errors.NotFound:
            logging.warning("Сообщение не найдено, либо оно уже было удалено ранее.")
        except Exception as error:
            logging.error(f"При попытке удаления сообщения возникла непредвиденная ошибка: {error}.")

    async def safe_fetch_message(self, message_id):
        channel = self.client.get_channel(config.COMMON_DISCUSSION_CHANNEL)
        try:
            fetched_message = await channel.fetch_message(message_id)
            return fetched_message
        except nextcord.NotFound:
            logging.info("Сообщение с предупреждением отсутствует, видимо, оно было ранее удалено вручную.")
        except Exception as error:
            logging.error(f"При попытке получения сообщения возникла непредвиденная ошибка: {error}.")

    async def check_spam(self, message):
        user_id = message.author.id
        if user_id not in self.user_message_statistics:
            self.user_message_statistics[user_id] = deque(maxlen=config.MAX_IMAGES)
        self.user_message_statistics[user_id].append(message.created_at.timestamp())
        if user_id in self.user_message_statistics and len(self.user_message_statistics[user_id]) == config.MAX_IMAGES:
            oldest_message_time = self.user_message_statistics[user_id].popleft()
            current_time = message.created_at.timestamp()
            if current_time - oldest_message_time <= config.TIME_LIMIT:
                self.muted_users[user_id] = {'channel': message.channel, 'reason': MUTE_REASONS['SPAM']}
                await self.mute_user(message, MUTE_REASONS['SPAM'])
                spam_initial_time = datetime.fromtimestamp(current_time - config.TIME_LIMIT)
                async for item in message.channel.history(limit=None, after=spam_initial_time):
                    if item.author == message.author:
                        await self.delete_message(item)
                self.user_message_statistics.pop(user_id, None)
                return True

    async def check_nsfw(self, message, message_images_urls):
        user_id = message.author.id
        for image_url in message_images_urls:
            if await self.is_image_nsfw(image_url):
                self.muted_users[user_id] = {'channel': message.channel, 'reason': MUTE_REASONS['NSFW']}
                await self.mute_user(message, MUTE_REASONS['NSFW'])
                await self.delete_message(message)
                logging.info(f"Изображение по адресу {image_url} содержит NSFW-контент и было удалено.")
                return True

    async def check_gifs(self, message, message_images_urls):
        gif_extension_pattern = re.compile(r"tenor\.com|giphy\.com|\.gif($|\?|&)")
        if any(gif_extension_pattern.search(image_url) for image_url in message_images_urls):
            user_id = message.author.id
            current_time = datetime.now()
            cooldown = timedelta(seconds=config.GIF_COOLDOWN_DURATION)
            if user_id in self.users_gifs and current_time - self.users_gifs[user_id].get('time') < cooldown:
                if self.users_gifs[user_id].get('warning_id'):
                    previous_warning_id = self.users_gifs[user_id].get('warning_id')
                    previous_warning_message = await self.safe_fetch_message(previous_warning_id)
                    if previous_warning_message:
                        await self.delete_message(previous_warning_message)
                warning_message = await message.channel.send(**messages.custom_embed(
                    title="💢 It's time to stop! 💢",
                    description=f"Уважаемый {message.author.mention}! Ваш бесплатный пробный период использования "
                                f"гифок на данный момент закончился. Для продления насыпьте костей или сена в "
                                f"кормушку модераторам.",
                    color="red"))
                self.users_gifs[user_id]['warning_id'] = warning_message.id
                await self.delete_message(message)
            else:
                self.users_gifs[user_id] = {'time': current_time, 'warning_id': None}

    async def check_unwanted_content(self, message, message_images_urls):
        is_spam = await self.check_spam(message)
        is_nsfw = await self.check_nsfw(message, message_images_urls)
        if is_spam or is_nsfw:
            return True
        if self.is_gif_limits and message.channel.id == config.COMMON_DISCUSSION_CHANNEL:
            await self.check_gifs(message, message_images_urls)

    @tasks.loop(minutes=10)
    async def purge_gif_warnings(self):
        for user_id, gif_info in self.users_gifs.items():
            current_warning_id = gif_info.get('warning_id')
            if current_warning_id:
                current_warning_message = await self.safe_fetch_message(current_warning_id)
                if current_warning_message:
                    await self.delete_message(current_warning_message)
                    self.users_gifs[user_id]['warning_id'] = None

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not before.communication_disabled_until and after.communication_disabled_until:
            if after.id in self.muted_users.keys():
                channel = self.muted_users[after.id]['channel']
                reason_for_muting = self.muted_users[after.id]['reason']
                await channel.send(**messages.custom_embed(
                    title="❌ Здравствуйте, вам бан! ❌",
                    description=f"Абоба {after.mention} {reason_for_muting}! "
                                f"Теперь он улетает в мут, хорошенько подумать о своем поведении!",
                    color="red"
                ))
                self.muted_users.pop(after.id, None)

    @nextcord.slash_command(description="Ограничения на использование гифок")
    @application_checks.has_role(config.ADMIN_ROLE)
    async def gif_limits(
            self,
            interaction: nextcord.Interaction,
            toggle: str = nextcord.SlashOption(
                description="Статус ограничений",
                choices={"установить": "on", "отменить": "off"}
            )):
        if toggle == "on":
            self.is_gif_limits = True
            if not self.purge_gif_warnings.is_running():
                self.purge_gif_warnings.start()
        elif toggle == "off":
            self.is_gif_limits = False
            self.purge_gif_warnings.stop()
            self.users_gifs.clear()
        status = "установлено" if toggle == "on" else "отменено"
        await interaction.response.send_message(**messages.custom_embed(
            description=f"Ограничение на использование гифок {status}."
        ))
        logging.info(f'Ограничение на использование гифок {status}.')


def setup(client):
    client.add_cog(ImageModerator(client))

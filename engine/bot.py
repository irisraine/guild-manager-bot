import nextcord
from nextcord.ext import commands, application_checks
import logging
import engine.config as config
import engine.utils as utils
import engine.views as views
import engine.messages as messages

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='&', intents=intents, default_guild_ids=[config.GUILD_ID])


@client.event
async def on_message(message):
    if message.channel.id in config.ANNOUNCEMENT_CHANNELS:
        if publisher := client.get_cog('Publisher'):
            return await publisher.publish_announcement_message(message)

    if message.author.bot and message.channel.id not in config.BOTS_ALLOWED_CHANNELS:
        return

    is_privileged = (
            message.author.bot or
            any(role.id in (config.ADMIN_ROLE, config.MODERATOR_ROLE) for role in message.author.roles)
    )

    if not is_privileged and message.channel.id in config.COMMANDS_ONLY_CHANNELS:
        if commands_only := client.get_cog('CommandsOnly'):
            return await commands_only.check_is_command(message)

    message_media_urls = utils.get_attached_media(message)
    is_message_in_media_only_channel = message.channel.id in config.MEDIA_ONLY_CHANNELS
    is_message_in_auto_threading_channel = message.channel.id in config.AUTO_THREADING_CHANNELS
    is_message_in_no_moderation_channel = message.channel.id in config.NO_MODERATION_CHANNELS
    if message_media_urls:
        if image_moderator := client.get_cog('ImageModerator'):
            images = message_media_urls['images']
            if not is_privileged and not is_message_in_no_moderation_channel and images:
                is_unwanted_content = await image_moderator.check_unwanted_content(message, images)
                if is_unwanted_content:
                    return
    elif not is_privileged and is_message_in_media_only_channel and not message.thread:
        try:
            return await message.delete()
        except nextcord.errors.NotFound:
            logging.warning("Сообщение не найдено, либо оно уже было удалено ранее.")
    if is_message_in_auto_threading_channel and (thread_manager := client.get_cog('ThreadManager')):
        await thread_manager.create_thread(message)

    await client.process_commands(message)


@client.slash_command(description="Загрузить или выгрузить модули бота")
@application_checks.has_role(config.ADMIN_ROLE)
async def toggle_extension(
        interaction: nextcord.Interaction,
        extension: str = nextcord.SlashOption(
            name="extension",
            description="Выберите загружаемый или выгружаемый модуль",
            choices=utils.get_cogs_list()
        )
):
    extension_name = f'engine.cogs.{extension}'
    try:
        if extension_name in client.extensions:
            client.unload_extension(extension_name)
            await interaction.response.send_message(
                **messages.toggle_extension(action="off", extension=extension)
            )
            logging.info(f'Модуль {extension} отключен.')
        else:
            client.load_extension(extension_name)
            await interaction.response.send_message(
                **messages.toggle_extension(action="on", extension=extension)
            )
            logging.info(f'Модуль {extension} успешно активирован.')
    except Exception as error:
        await interaction.response.send_message(
            **messages.toggle_extension(extension=extension, is_valid=False), ephemeral=True)
        logging.error(f'Ошибка при попытке загрузки модуля {extension}. Дополнительная информация: {error}')


@client.slash_command(description="Панель конфигурации")
@application_checks.has_permissions(administrator=True)
async def settings(interaction: nextcord.Interaction):
    await interaction.response.send_message(
        **messages.settings(),
        view=views.SettingsMenuView()
    )


@client.event
async def on_application_command_error(interaction: nextcord.Interaction, error):
    handled_errors = (
        application_checks.ApplicationMissingAnyRole,
        application_checks.ApplicationMissingRole,
        application_checks.ApplicationMissingPermissions
    )
    if isinstance(error, handled_errors):
        await interaction.response.send_message(**messages.error())
    else:
        logging.error(f"При использовании команды произошла непредвиденная ошибка: {error}")


@client.event
async def on_ready():
    logging.info(f'Бот залогинен под именем: {client.user.name}')

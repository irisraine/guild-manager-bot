import nextcord
from nextcord.ext import commands, application_checks
import logging
import engine.config as config
import engine.utils as utils

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='&', intents=intents, default_guild_ids=[config.GUILD_ID])


@client.event
async def on_message(message):
    if message.channel.id in config.ANNOUNCEMENT_CHANNELS:
        if publisher := client.get_cog('Publisher'):
            return await publisher.publish_announcement_message(message)

    if message.author.bot:
        return

    is_admin = message.author.guild_permissions.administrator

    if not is_admin and message.channel.id in config.COMMANDS_ONLY_CHANNELS:
        if commands_only := client.get_cog('CommandsOnly'):
            return await commands_only.check_is_command(message)

    message_media_urls = utils.get_attached_media(message)
    is_message_in_media_only_channel = message.channel.id in config.MEDIA_ONLY_CHANNELS
    if message_media_urls:
        if not is_admin and message_media_urls['images'] and (image_moderator := client.get_cog('ImageModerator')):
            is_unwanted_content = await image_moderator.check_unwanted_content(message, message_media_urls['images'])
            if is_unwanted_content:
                return
        if is_message_in_media_only_channel and (thread_manager := client.get_cog('ThreadManager')):
            await thread_manager.create_thread(message)
    elif not is_admin and is_message_in_media_only_channel and not message.thread:
        try:
            await message.delete()
        except nextcord.errors.NotFound:
            logging.warning("Сообщение не найдено, либо оно уже было удалено ранее.")

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
                embed=nextcord.Embed(
                    description=f"Модуль **{extension}** отключен.",
                    colour=nextcord.Color.green()))
            logging.info(f'Модуль {extension} отключен.')
        else:
            client.load_extension(extension_name)
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    description=f"Модуль **{extension}** успешно активирован.",
                    colour=nextcord.Color.green()))
            logging.info(f'Модуль {extension} успешно активирован.')
    except Exception as error:
        await interaction.response.send_message(
            embed=nextcord.Embed(
                description=f"Ошибка при попытке загрузки модуля {extension}.",
                colour=nextcord.Color.red()), ephemeral=True)
        logging.error(f'Ошибка при попытке загрузки модуля {extension}. Дополнительная информация: {error}')


@client.event
async def on_application_command_error(interaction: nextcord.Interaction, error):
    handled_errors = (application_checks.ApplicationMissingAnyRole, application_checks.ApplicationMissingRole)
    if isinstance(error, handled_errors):
        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Ошибка",
                description="У вас недостаточно прав для использования данной команды!",
                colour=nextcord.Color.red()), ephemeral=True
        )
    else:
        logging.error(f"При использовании команды произошла непредвиденная ошибка: {error}")


@client.event
async def on_ready():
    logging.info(f'Бот залогинен под именем: {client.user.name}')

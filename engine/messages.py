import nextcord
import engine.config as config


ERROR_HEADER = "Ошибка"
SUCCESS_HEADER = "Успешно"


class MessageContainer:
    def __init__(self, title=None, description=None, image_path=None, color=None):
        if color == "red":
            color = nextcord.Color.red()
        else:
            color = nextcord.Color.red() if title == ERROR_HEADER else nextcord.Color.green()
        self.__embed = nextcord.Embed(
            title=title,
            description=description,
            colour=color,
        )
        if not image_path:
            image_path = config.SEPARATOR
        image_name = image_path.split('/')[-1]
        image_attachment = f"attachment://{image_name}"
        self.__embed.set_image(url=image_attachment)
        self.__image = nextcord.File(image_path, filename=image_name)

    @property
    def embed(self):
        return self.__embed

    @property
    def image(self):
        return self.__image


def toggle_extension(action=None, extension=None, is_valid=True):
    title = SUCCESS_HEADER if is_valid else ERROR_HEADER
    if not is_valid:
        description = f"Ошибка при попытке загрузки модуля {extension}."
    else:
        description = f"Модуль **{extension}** "
        if action == "on":
            description += "успешно активирован."
        elif action == "off":
            description += "отключен."
    embed_message = MessageContainer(
        title=title,
        description=description,
    )
    return {'embed': embed_message.embed, 'file': embed_message.image}


def setup():
    embed_message = MessageContainer(
        title="Панель конфигурации",
        description="Настройки бота, позволяющие установить специальные свойства для каналов и ролей. "
                    "Доступно только для администраторов.",
        image_path=config.SETUP_MENU_IMAGE
    )
    return {'embed': embed_message.embed, 'file': embed_message.image}


def special_channels(category, channels_list):
    title = "Cписок"
    description = ""
    if not channels_list:
        channels_list_with_mentions = "*Список пуст! Ни одного канала еще не добавлено.*"
    else:
        channels_list_with_mentions = "\n".join([f"- <#{channel}> — **ID**: {channel}" for channel in channels_list])
    if category == "media_only":
        title += " медиаканалов"
        description += ("Каналы, в которых пользователи могут размещать только медиаконтент: изображения и видео. "
                        "Текстовые сообщения автоматически удаляются, за исключением тех, которые созданы в ветках.\n\n"
                        f"{channels_list_with_mentions}")
        image_path = config.MEDIA_ONLY_IMAGE
    elif category == "commands_only":
        title += " каналов для команд"
        description += ("Технические каналы, в которых допускается использование только команд для ботов. "
                        "Любые другие сообщения автоматически удаляются.\n\n"
                        f"{channels_list_with_mentions}")
        image_path = config.COMMANDS_ONLY_IMAGE
    elif category == "auto_threading":
        title += " каналов со включенным автотредингом"
        description += ("Каналы, в которых после размещения любого сообщения бот автоматически создает для него "
                        "свою ветку.\n\n"
                        f"{channels_list_with_mentions}")
        image_path = config.AUTO_THREADING_IMAGE
    elif category == "no_moderation":
        title += " каналов без модерации медиаконтента"
        description += ("Каналы, в которых отключена система автоматической модерации контента, проверяющая "
                        "наличие NSFW в прилагаемых изображениях.\n\n"
                        f"{channels_list_with_mentions}")
        image_path = config.NO_MODERATION_IMAGE
    elif category == "bots_allowed":
        title += " каналов для ботов"
        description += ("Каналы, в которых сообщения размещаются преимущественно с помощью ботов.\n\n"
                        f"{channels_list_with_mentions}\n\n"
                        f"Включение канала в данный список позволяет разрешить дополнительную настройку обработки "
                        f"сообщений, в частности, разрешить создание тредов для сообщений от ботов, что в обычных "
                        f"условиях невозможно.")
        image_path = config.BOTS_ALLOWED_IMAGE
    elif category == "announcement":
        title += " новостных каналов"
        description += ("Каналы, сообщения в которых после публикации автоматически рассылаются на другие серверы, "
                        "оформившие подписку на них.\n\n"
                        f"{channels_list_with_mentions}")
        image_path = config.ANNOUNCEMENT_IMAGE
    embed_message = MessageContainer(
        title=title,
        description=description,
        image_path=image_path
    )
    return {'embed': embed_message.embed, 'file': embed_message.image}


def special_channels_confirmation(action=None, channel_id=None, is_valid=True, reason=None):
    title = SUCCESS_HEADER if is_valid else ERROR_HEADER
    image_path = config.SUCCESS_IMAGE if is_valid else config.ERROR_IMAGE
    description = "Канал "
    if action == "add":
        if not is_valid:
            description += " не удалось добавить. "
            if reason == "typo":
                description += "Вы ошиблись при вводе ID канала. Он должен состоять из 18 или 19 цифр."
            elif reason == "not_exist":
                description += "Вы ошиблись при вводе ID канала. Такого канала не существует на нашем сервере!"
            elif reason == "already_added":
                description += "Этот канал уже присутствует в списке, повторно его добавить нельзя."
        else:
            description += f" <#{channel_id}> успешно добавлен в список."
    if action == "remove":
        if not is_valid:
            description += " не удалось удалить. "
            if reason == "typo":
                description += "Вы ошиблись при вводе ID канала. Он должен состоять из 18 или 19 цифр."
            elif reason == "already_removed":
                description += "Этот канал уже отсутствует в списке."
        else:
            description += f" <#{channel_id}> успешно удален из списка."
    embed_message = MessageContainer(
        title=title,
        description=description,
        image_path=image_path
    )
    return {'embed': embed_message.embed, 'file': embed_message.image, 'ephemeral': True}


def authorized_bands(roles_list):
    if not roles_list:
        roles_list_list_with_mentions = "*Список пуст! Ни одной банды пока еще не авторизовано.*"
    else:
        roles_list_list_with_mentions = "\n".join([f"- <@&{role}> — **ID**: {role}" for role in roles_list])
    embed_message = MessageContainer(
        title="Список авторизованных банд",
        description="На настоящий момент на нашем сервере присутствуют следующие банды: \n\n"
                    f"{roles_list_list_with_mentions}\n\n"
                    "С помощью данной панели можно авторизовать новую банду и ее лидера, или деавторизовать "
                    "уже существующую. Авторизация банды даст право предводителю самостоятельно выдавать "
                    "пользователям роль участника своей банды.\n\n"
                    "При деавторизации банды происходит автоматическая деавторизация ее предводителя.",
        image_path=config.BAND_AUTHORIZATION_IMAGE
    )
    return {'embed': embed_message.embed, 'file': embed_message.image}


def authorized_bands_confirmation(action=None, band_role_id=None, is_valid=True, role_category=None, reason=None):
    title = SUCCESS_HEADER if is_valid else ERROR_HEADER
    image_path = config.SUCCESS_IMAGE if is_valid else config.ERROR_IMAGE
    description = ""
    if action == "add":
        if not is_valid:
            description += "Банду не удалось авторизовать. "
            role_category_text = "бандитской роли" if role_category == "band" else "роли предводителя банды"
            if reason == "typo":
                description += (f"Вы ошиблись при вводе ID {role_category_text}. "
                                "Он должен состоять из 18 или 19 цифр.")
            elif reason == "not_exist":
                description += (f"Вы ошиблись при вводе ID {role_category_text}. "
                                f"Такой роли не существует на нашем сервере!")
            elif reason == "already_added":
                if role_category == "band":
                    description += ("Этот ID бандитской роли уже присутствует в списке банд, "
                                    "повторно его добавить нельзя.")
                elif role_category == "band_leader":
                    description += ("Этот ID принадлежит предводителю другой банды. Один и тот же участник не может "
                                    "одновременно возглавлять несколько банд!")
        else:
            description += f"Банда <@&{band_role_id}> и ее предводитель успешно авторизованы!"
    if action == "remove":
        if not is_valid:
            description += "Банду не удалось деавторизовать. "
            if reason == "typo":
                description += "Вы ошиблись при вводе ID бандитской роли. Он должен состоять из 18 или 19 цифр."
            elif reason == "already_removed":
                description += "Эта банда не была авторизована ранее и отсутствует в списке."
        else:
            description += (f"Банда <@&{band_role_id}> и ее предводитель успешно деавторизованы. "
                            f"Память о ней сотрут пески времен.")
    embed_message = MessageContainer(
        title=title,
        description=description,
        image_path=image_path
    )
    return {'embed': embed_message.embed, 'file': embed_message.image, 'ephemeral': True}


def custom_embed_message(title=None, description=None, image_path=None, color="green"):
    embed_message = MessageContainer(
        title=title,
        description=description,
        image_path=image_path,
        color=color
    )
    return {'embed': embed_message.embed, 'file': embed_message.image}


def error(description=None):
    description = "У вас недостаточно прав для использования данной команды!" if not description else description
    embed_message = MessageContainer(
        title=ERROR_HEADER,
        description=description,
        image_path=config.ERROR_IMAGE
    )
    return {'embed': embed_message.embed, 'file': embed_message.image, 'ephemeral': True}


def admin_option_only_warning():
    embed_message = MessageContainer(
        title=ERROR_HEADER,
        description="Использовать опции конфигурационной панели могут только администраторы сервера.",
        image_path=config.ERROR_IMAGE
    )
    return {'embed': embed_message.embed, 'file': embed_message.image}

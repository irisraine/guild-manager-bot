import nextcord
import engine.bot as bot
import engine.messages as messages
import engine.config as config
import engine.utils as utils


class SetupMenuView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
        else:
            await interaction.response.send_message(**messages.admin_option_only_warning(), ephemeral=True)
            return False

    @nextcord.ui.select(
        placeholder="Выбери нужную опцию",
        options=[
            nextcord.SelectOption(
                label="Автотрединг",
                value="auto_threading",
                description="Список каналов с автоматическим созданием веток",
                emoji=config.CATEGORY_EMOJI["auto_threading"]),
            nextcord.SelectOption(
                label="Авторизация банд",
                value="band",
                description="Право выдавать роль участника банды",
                emoji=config.CATEGORY_EMOJI["band"]),
            nextcord.SelectOption(
                label="Медиа-каналы",
                value="media_only",
                description="Список каналов только для медиаконтента (картинки и видео)",
                emoji=config.CATEGORY_EMOJI["media_only"]),
            nextcord.SelectOption(
                label="Каналы для команд",
                value="commands_only",
                description="Список технических каналов только для команд",
                emoji=config.CATEGORY_EMOJI["commands_only"]),
            nextcord.SelectOption(
                label="Немодерируемые каналы",
                value="no_moderation",
                description="Список каналов с отключенной системой модерации контента",
                emoji=config.CATEGORY_EMOJI["no_moderation"]),
            nextcord.SelectOption(
                label="Каналы для ботов",
                value="bots_allowed",
                description="Список каналов с контентом от ботов",
                emoji=config.CATEGORY_EMOJI["bots_allowed"]),
        ]
    )
    async def select_setup_menu_callback(self, select, interaction: nextcord.Interaction):
        admin_actions = {
            "auto_threading": {
                "message": messages.special_channels(category="auto_threading", channels_list=config.AUTO_THREADING_CHANNELS),
                "view": ChannelView(category="auto_threading")
            },
            "band": {
                "message": messages.authorized_bands(config.BAND_ROLES),
                "view": BandsView()
            },
            "media_only": {
                "message": messages.special_channels(category="media_only", channels_list=config.MEDIA_ONLY_CHANNELS),
                "view": ChannelView(category="media_only")
            },
            "commands_only": {
                "message": messages.special_channels(category="commands_only", channels_list=config.COMMANDS_ONLY_CHANNELS),
                "view": ChannelView(category="commands_only")
            },
            "no_moderation": {
                "message": messages.special_channels(category="no_moderation", channels_list=config.NO_MODERATION_CHANNELS),
                "view": ChannelView(category="no_moderation")
            },
            "bots_allowed": {
                "message": messages.special_channels(category="bots_allowed", channels_list=config.BOTS_ALLOWED_CHANNELS),
                "view": ChannelView(category="bots_allowed")
            },
        }
        await interaction.response.defer()
        await interaction.edit_original_message(
            **admin_actions[select.values[0]]["message"],
            view=admin_actions[select.values[0]]["view"]
        )

    @nextcord.ui.button(label="Закрыть панель конфигурации", style=nextcord.ButtonStyle.gray, emoji="❌")
    async def close_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        await interaction.delete_original_message()


class SetupActionBasicView(nextcord.ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(timeout=None, *args, **kwargs)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
        else:
            await interaction.response.send_message(**messages.admin_option_only_warning(), ephemeral=True)
            return False

    @nextcord.ui.button(label="Вернуться в панель конфигурации", style=nextcord.ButtonStyle.gray, emoji="◀️", row=2)
    async def return_to_setup_menu_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        await interaction.edit_original_message(
            **messages.setup(),
            view=SetupMenuView()
        )

    @nextcord.ui.button(label="Закрыть", style=nextcord.ButtonStyle.gray, emoji="❌", row=2)
    async def close_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        await interaction.delete_original_message()


class ChannelView(SetupActionBasicView):
    def __init__(self, category):
        super().__init__()
        self.category = category

    @nextcord.ui.button(label="Добавить канал", style=nextcord.ButtonStyle.green, emoji="➕")
    async def set_cooldown_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(ChannelModal(category=self.category, action="add"))

    @nextcord.ui.button(label="Удалить канал", style=nextcord.ButtonStyle.red, emoji="➖")
    async def default_cooldown_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(ChannelModal(category=self.category, action="remove"))


class ChannelModal(nextcord.ui.Modal):
    CATEGORIES = {
        'auto_threading': (config.AUTO_THREADING_CHANNELS, config.AUTO_THREADING_CHANNELS_JSON),
        'commands_only': (config.COMMANDS_ONLY_CHANNELS, config.COMMANDS_ONLY_CHANNELS_JSON),
        'media_only': (config.MEDIA_ONLY_CHANNELS, config.MEDIA_ONLY_CHANNELS_JSON),
        'no_moderation': (config.NO_MODERATION_CHANNELS, config.NO_MODERATION_CHANNELS_JSON),
        'bots_allowed': (config.BOTS_ALLOWED_CHANNELS, config.BOTS_ALLOWED_CHANNELS_JSON)
    }

    def __init__(self, category, action):
        self.category = category
        self.action = action
        super().__init__("Добавить канал" if self.action == "add" else "Удалить канал")

        self.channel = nextcord.ui.TextInput(
            label="ID канала",
            required=True,
            style=nextcord.TextInputStyle.short
        )
        self.add_item(self.channel)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.defer()
        if self.action == "add":
            if not utils.validator(self.channel.value):
                return await interaction.followup.send(
                    **messages.special_channels_confirmation(
                        channel=self.channel.value, action=self.action, is_valid=False, reason="typo"
                    ))
            if int(self.channel.value) not in self.CATEGORIES[self.category][0]:
                channel = bot.client.get_channel(int(self.channel.value))
                if channel:
                    self.CATEGORIES[self.category][0].append(int(self.channel.value))
                    utils.json_safewrite(
                        filepath=self.CATEGORIES[self.category][1],
                        data={"channels": self.CATEGORIES[self.category][0]}
                    )
                    await interaction.followup.send(
                        **messages.special_channels_confirmation(
                            channel=self.channel.value, action=self.action
                        ))
                else:
                    await interaction.followup.send(
                        **messages.special_channels_confirmation(
                            channel=self.channel.value, action=self.action, is_valid=False, reason="not_exist"
                        ))
            else:
                await interaction.followup.send(
                    **messages.special_channels_confirmation(
                        channel=self.channel.value, action=self.action, is_valid=False, reason="already_added"
                    ))
        if self.action == "remove":
            if not utils.validator(self.channel.value):
                return await interaction.followup.send(
                    **messages.special_channels_confirmation(
                        channel=self.channel.value, action=self.action, is_valid=False, reason="typo"
                    ))
            if int(self.channel.value) in self.CATEGORIES[self.category][0]:
                self.CATEGORIES[self.category][0].remove(int(self.channel.value))
                utils.json_safewrite(
                    filepath=self.CATEGORIES[self.category][1],
                    data={"channels": self.CATEGORIES[self.category][0]}
                )
                await interaction.followup.send(
                    **messages.special_channels_confirmation(
                        channel=self.channel.value, action=self.action
                    ))
            else:
                await interaction.followup.send(
                    **messages.special_channels_confirmation(
                        channel=self.channel.value, action=self.action, is_valid=False, reason="already_removed"
                    ))


class BandsView(SetupActionBasicView):
    def __init__(self):
        super().__init__()

    @nextcord.ui.button(label="Авторизовать банду", style=nextcord.ButtonStyle.green, emoji="➕")
    async def set_cooldown_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(BandsAddModal())

    @nextcord.ui.button(label="Деавторизовать банду", style=nextcord.ButtonStyle.red, emoji="➖")
    async def default_cooldown_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(BandsRemoveModal())


class BandsAddModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Авторизовать банду и ее предводителя")

        self.band_role = nextcord.ui.TextInput(
            label="ID бандитской роли",
            required=True,
            style=nextcord.TextInputStyle.short
        )
        self.add_item(self.band_role)
        self.band_leader_role = nextcord.ui.TextInput(
            label="ID роли предводителя банды",
            required=True,
            style=nextcord.TextInputStyle.short
        )
        self.add_item(self.band_leader_role)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.defer()
        if not utils.validator(self.band_role.value):
            return await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    band_role=self.band_role.value, action="add", is_valid=False, role_category="band_role", reason="typo"
                ))
        if not utils.validator(self.band_leader_role.value):
            return await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    band_role=self.band_role.value, action="add", is_valid=False, role_category="band_role_leader", reason="typo"
                ))
        if int(self.band_role.value) not in config.BAND_ROLES and int(self.band_leader_role.value) not in config.BAND_LEADERS_ROLES:
            band_role = interaction.guild.get_role(int(self.band_role.value))
            band_leader_role = interaction.guild.get_role(int(self.band_leader_role.value))
            if band_role and band_leader_role:
                config.BAND_ROLES.append(int(self.band_role.value))
                config.BAND_LEADERS_ROLES.append(int(self.band_leader_role.value))
                utils.json_safewrite(
                    filepath=config.BANDS_JSON,
                    data={
                        "band_roles": config.BAND_ROLES,
                        "band_leader_roles": config.BAND_LEADERS_ROLES
                    }
                )
                await interaction.followup.send(
                    **messages.authorized_bands_confirmation(
                        band_role=self.band_role.value, action="add"
                    ))
            elif not band_role:
                return await interaction.followup.send(
                    **messages.authorized_bands_confirmation(
                        band_role=self.band_role.value, action="add", is_valid=False, role_category="band_role", reason="not_exist"
                    ))
            elif not band_leader_role:
                return await interaction.followup.send(
                    **messages.authorized_bands_confirmation(
                        band_role=self.band_role.value, action="add", is_valid=False, role_category="band_leader_role", reason="not_exist"
                    ))
        elif int(self.band_role.value) in config.BAND_ROLES:
            return await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    band_role=self.band_role.value, action="add", is_valid=False, role_category="band_role", reason="already_added"
                ))
        elif int(self.band_leader_role.value) in config.BAND_LEADERS_ROLES:
            return await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    band_role=self.band_role.value, action="add", is_valid=False, role_category="band_leader_role", reason="already_added"
                ))


class BandsRemoveModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Деавторизовать банду")

        self.band_role = nextcord.ui.TextInput(
            label="ID бандитской роли",
            required=True,
            style=nextcord.TextInputStyle.short
        )
        self.add_item(self.band_role)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.defer()
        if not utils.validator(self.band_role.value):
            return await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    band_role=self.band_role.value, action="remove", is_valid=False, reason="typo"
                ))
        if int(self.band_role.value) in config.BAND_ROLES:
            role_index = config.BAND_ROLES.index(int(self.band_role.value))
            config.BAND_ROLES.remove(int(self.band_role.value))
            del config.BAND_LEADERS_ROLES[role_index]
            utils.json_safewrite(
                filepath=config.BANDS_JSON,
                data={
                    "band_roles": config.BAND_ROLES,
                    "band_leader_roles": config.BAND_LEADERS_ROLES
                }
            )
            await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    band_role=self.band_role.value, action="remove"
                ))
        else:
            await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    band_role=self.band_role.value, action="remove", is_valid=False, reason="already_removed"
                ))

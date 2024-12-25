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
                value="authorize_band",
                description="Право выдавать роль участника банды",
                emoji=config.CATEGORY_EMOJI["authorize_band"]),
            nextcord.SelectOption(
                label="Медиа-каналы",
                value="media_only",
                description="Список каналов только для картинок и видео",
                emoji=config.CATEGORY_EMOJI["media_only"]),
            nextcord.SelectOption(
                label="Каналы для команд",
                value="commands_only",
                description="Список технических каналов только для команд",
                emoji=config.CATEGORY_EMOJI["commands_only"]),
            nextcord.SelectOption(
                label="Немодерируемые каналы",
                value="no_moderation",
                description="Список каналов с отключенной системой модерации",
                emoji=config.CATEGORY_EMOJI["no_moderation"]),
            nextcord.SelectOption(
                label="Каналы для ботов",
                value="bots_allowed",
                description="Список каналов с контентом от ботов",
                emoji=config.CATEGORY_EMOJI["bots_allowed"]),
            nextcord.SelectOption(
                label="Новостные каналы",
                value="announcement",
                description="Список каналов со включенной рассылкой",
                emoji=config.CATEGORY_EMOJI["announcement"]),
        ]
    )
    async def select_setup_menu_callback(self, select, interaction: nextcord.Interaction):
        setup_actions = {
            "auto_threading": {
                "message": messages.special_channels(category="auto_threading"),
                "view": SpecialChannelsView(category="auto_threading")
            },
            "authorize_band": {
                "message": messages.authorized_bands(),
                "view": AuthorizedBandsView()
            },
            "media_only": {
                "message": messages.special_channels(category="media_only"),
                "view": SpecialChannelsView(category="media_only")
            },
            "commands_only": {
                "message": messages.special_channels(category="commands_only"),
                "view": SpecialChannelsView(category="commands_only")
            },
            "no_moderation": {
                "message": messages.special_channels(category="no_moderation"),
                "view": SpecialChannelsView(category="no_moderation")
            },
            "bots_allowed": {
                "message": messages.special_channels(category="bots_allowed"),
                "view": SpecialChannelsView(category="bots_allowed")
            },
            "announcement": {
                "message": messages.special_channels(category="announcement"),
                "view": SpecialChannelsView(category="announcement")
            },
        }
        await interaction.response.defer()
        await interaction.edit_original_message(
            **setup_actions[select.values[0]]["message"],
            view=setup_actions[select.values[0]]["view"]
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


class SpecialChannelsView(SetupActionBasicView):
    def __init__(self, category):
        super().__init__()
        self.category = category

    @nextcord.ui.button(label="Добавить канал", style=nextcord.ButtonStyle.green, emoji="➕")
    async def add_special_channel_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(SpecialChannelsModal(category=self.category, action="add"))

    @nextcord.ui.button(label="Удалить канал", style=nextcord.ButtonStyle.red, emoji="➖")
    async def remove_special_channel_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(SpecialChannelsModal(category=self.category, action="remove"))


class SpecialChannelsModal(nextcord.ui.Modal):
    def __init__(self, category, action):
        self.category = category
        self.action = action
        super().__init__("Добавить канал" if self.action == "add" else "Удалить канал")

        self.special_channel = nextcord.ui.TextInput(
            label="ID канала",
            required=True,
            style=nextcord.TextInputStyle.short
        )
        self.add_item(self.special_channel)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.defer()
        special_channel_id = utils.get_valid_id(self.special_channel.value)
        if self.action == "add":
            if not special_channel_id:
                return await interaction.followup.send(
                    **messages.special_channels_confirmation(
                        action=self.action, is_valid=False, reason="typo"
                    ))
            if special_channel_id not in config.SPECIAL_CHANNELS_CATEGORIES[self.category]['ids']:
                channel = bot.client.get_channel(special_channel_id)
                if channel:
                    config.SPECIAL_CHANNELS_CATEGORIES[self.category]['ids'].append(special_channel_id)
                    utils.json_safewrite(
                        filepath=config.SPECIAL_CHANNELS_CATEGORIES[self.category]['json_file'],
                        data={"channels": config.SPECIAL_CHANNELS_CATEGORIES[self.category]['ids']}
                    )
                    await interaction.followup.send(
                        **messages.special_channels_confirmation(
                            action=self.action, channel_id=special_channel_id
                        ))
                else:
                    await interaction.followup.send(
                        **messages.special_channels_confirmation(
                            action=self.action, is_valid=False, reason="not_exist"
                        ))
            else:
                await interaction.followup.send(
                    **messages.special_channels_confirmation(
                        action=self.action, is_valid=False, reason="already_added"
                    ))
        if self.action == "remove":
            if not special_channel_id:
                return await interaction.followup.send(
                    **messages.special_channels_confirmation(
                        action=self.action, is_valid=False, reason="typo"
                    ))
            if special_channel_id in config.SPECIAL_CHANNELS_CATEGORIES[self.category]['ids']:
                config.SPECIAL_CHANNELS_CATEGORIES[self.category]['ids'].remove(special_channel_id)
                utils.json_safewrite(
                    filepath=config.SPECIAL_CHANNELS_CATEGORIES[self.category]['json_file'],
                    data={"channels": config.SPECIAL_CHANNELS_CATEGORIES[self.category]['ids']}
                )
                await interaction.followup.send(
                    **messages.special_channels_confirmation(
                        action=self.action, channel_id=special_channel_id
                    ))
            else:
                await interaction.followup.send(
                    **messages.special_channels_confirmation(
                        action=self.action, is_valid=False, reason="already_removed"
                    ))


class AuthorizedBandsView(SetupActionBasicView):
    def __init__(self):
        super().__init__()

    @nextcord.ui.button(label="Авторизовать банду", style=nextcord.ButtonStyle.green, emoji="➕")
    async def authorize_band_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(AuthorizedBandsAddModal())

    @nextcord.ui.button(label="Деавторизовать банду", style=nextcord.ButtonStyle.red, emoji="➖")
    async def deauthorize_band_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(AuthorizedBandsRemoveModal())


class AuthorizedBandsAddModal(nextcord.ui.Modal):
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
        band_role_id = utils.get_valid_id(self.band_role.value)
        band_leader_role_id = utils.get_valid_id(self.band_leader_role.value)
        if not band_role_id:
            return await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    action="add", is_valid=False, role_category="band", reason="typo"
                ))
        if not band_leader_role_id:
            return await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    action="add", is_valid=False, role_category="band_leader", reason="typo"
                ))
        if band_role_id not in config.AUTHORIZED_BAND_ROLES and band_leader_role_id not in config.AUTHORIZED_BAND_LEADERS_ROLES:
            band_role = interaction.guild.get_role(band_role_id)
            band_leader_role = interaction.guild.get_role(band_leader_role_id)
            if band_role and band_leader_role:
                config.AUTHORIZED_BAND_ROLES.append(band_role_id)
                config.AUTHORIZED_BAND_LEADERS_ROLES.append(band_leader_role_id)
                utils.json_safewrite(
                    filepath=config.AUTHORIZED_BANDS_JSON,
                    data={
                        "band_roles": config.AUTHORIZED_BAND_ROLES,
                        "band_leader_roles": config.AUTHORIZED_BAND_LEADERS_ROLES
                    }
                )
                await interaction.followup.send(
                    **messages.authorized_bands_confirmation(
                        action="add", band_role_id=band_role_id
                    ))
            elif not band_role:
                return await interaction.followup.send(
                    **messages.authorized_bands_confirmation(
                        action="add", is_valid=False, role_category="band", reason="not_exist"
                    ))
            elif not band_leader_role:
                return await interaction.followup.send(
                    **messages.authorized_bands_confirmation(
                        action="add", is_valid=False, role_category="band_leader", reason="not_exist"
                    ))
        elif band_role_id in config.AUTHORIZED_BAND_ROLES:
            return await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    action="add", is_valid=False, role_category="band", reason="already_added"
                ))
        elif band_leader_role_id in config.AUTHORIZED_BAND_LEADERS_ROLES:
            return await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    action="add", is_valid=False, role_category="band_leader", reason="already_added"
                ))


class AuthorizedBandsRemoveModal(nextcord.ui.Modal):
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
        band_role_id = utils.get_valid_id(self.band_role.value)
        if not band_role_id:
            return await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    action="remove", is_valid=False, reason="typo"
                ))
        if band_role_id in config.AUTHORIZED_BAND_ROLES:
            band_role_index = config.AUTHORIZED_BAND_ROLES.index(band_role_id)
            config.AUTHORIZED_BAND_ROLES.remove(band_role_id)
            del config.AUTHORIZED_BAND_LEADERS_ROLES[band_role_index]
            utils.json_safewrite(
                filepath=config.AUTHORIZED_BANDS_JSON,
                data={
                    "band_roles": config.AUTHORIZED_BAND_ROLES,
                    "band_leader_roles": config.AUTHORIZED_BAND_LEADERS_ROLES
                }
            )
            await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    action="remove", band_role_id=band_role_id
                ))
        else:
            await interaction.followup.send(
                **messages.authorized_bands_confirmation(
                    action="remove", is_valid=False, reason="already_removed"
                ))

import nextcord
from nextcord.ext import commands, application_checks
import engine.config as config
import engine.messages as messages


class TalkModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Отправка сообщения от лица бота")

        self.message_content = nextcord.ui.TextInput(
            label="Сообщение",
            required=True,
            placeholder="Текст сообщения",
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.message_content)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.defer()
        channel = interaction.guild.get_channel(config.COMMON_DISCUSSION_CHANNEL)
        await channel.send(self.message_content.value)
        await interaction.followup.send(
            **messages.custom_embed_message(description="Сообщение в салун отправлено!"),
            ephemeral=True
        )


class TalkView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
        else:
            await interaction.response.send_message(**messages.admin_option_only_warning(), ephemeral=True)
            return False

    @nextcord.ui.button(label="Сообщение", style=nextcord.ButtonStyle.blurple, emoji="🦌")
    async def send_message_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(TalkModal())

    @nextcord.ui.button(label="Закрыть", style=nextcord.ButtonStyle.gray, emoji="❌")
    async def close_panel_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.message.delete()


class Talk(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(description="Отправить сообщение от лица бота")
    @application_checks.has_role(config.ADMIN_ROLE)
    async def say(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            **messages.custom_embed_message(
                title="Сообщение в салун от лица Лесного Оленя",
                description="Лесной олень стал сильнее и умнее, по воле своего творца обретя дар разума и речи. "
                            "На что же он употребит обретенную мощь? С каким словом обратится к миру?"),
            view=TalkView()
        )


def setup(client):
    client.add_cog(Talk(client))

import nextcord
from nextcord import Interaction
from nextcord.ext import commands
import engine.config as config


TALK_PANEL_INITIAL_MESSAGE = ("Лесной олень стал сильнее и умнее, по воле своего творца обретя дар разума и речи. "
                              "На что же он употребит обретенную мощь? С каким словом обратится к миру?")
TALK_PANEL_USAGE_RESTRICTION = "Управлять Лесным оленем могут только те, чьи дороги пролегают меж звезд"
SUCCESSFUL_SENDING = "Сообщение в салун отправлено!"


class MessageByBot(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Отправка сообщения от лица бота")

        self.message_content = nextcord.ui.TextInput(
            label="Сообщение",
            required=True,
            placeholder="Текст сообщения",
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.message_content)

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        channel = interaction.guild.get_channel(config.COMMON_DISCUSSION_CHANNEL)
        await channel.send(self.message_content.value)
        await interaction.followup.send(SUCCESSFUL_SENDING, ephemeral=True)


class MessagePanel(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
        else:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    description=TALK_PANEL_USAGE_RESTRICTION,
                    colour=nextcord.Color.red()),
                ephemeral=True)
            return False

    @nextcord.ui.button(label="Сообщение", style=nextcord.ButtonStyle.blurple, emoji="🦌")
    async def send_message_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(MessageByBot())

    @nextcord.ui.button(label="Закрыть", style=nextcord.ButtonStyle.red, emoji="✖️")
    async def close_panel_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.message.delete()


class Talk(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def say(self, ctx):
        await ctx.send(
            embed=nextcord.Embed(
                description=TALK_PANEL_INITIAL_MESSAGE,
                colour=nextcord.Color.red()),
            view=MessagePanel()
        )


def setup(client):
    client.add_cog(Talk(client))

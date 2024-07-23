import nextcord
from nextcord.ext import commands, application_checks
import logging
import engine.config as config

ERROR_HEADER = "Ошибка"
UNABLE_TO_ASSIGN_ROLE_TO_BOT = "Боты не могут находиться в банде."
UNABLE_TO_ASSIGN_ROLE_TO_YOURSELF = ("Предводитель банды всегда состоит в ней, "
                                     "и он не может быть удален или добавлен повторно.")
NOT_A_LEADER = "Вы не являетесь предводителем ни одной из банд."
BAND_ROLE_SET = "✅ Вступление в банду"
BAND_ROLE_REMOVED = "❌ Исключение из банды"


class BandManager(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command()
    async def band(self, interaction: nextcord.Interaction):
        pass

    async def handle_role(self, interaction: nextcord.Interaction, member: nextcord.Member, action: str):
        if member.bot:
            await interaction.response.send_message(embed=nextcord.Embed(
                title=ERROR_HEADER,
                description=UNABLE_TO_ASSIGN_ROLE_TO_BOT,
                color=nextcord.Color.red()
            ), ephemeral=True)
            return
        if member.id == interaction.user.id:
            await interaction.response.send_message(embed=nextcord.Embed(
                title=ERROR_HEADER,
                description=UNABLE_TO_ASSIGN_ROLE_TO_YOURSELF,
                color=nextcord.Color.red()
            ), ephemeral=True)
            return

        user_roles_ids = [role.id for role in interaction.user.roles]
        band_leader_role_id = list(filter(lambda role_id: role_id in config.GROUP_LEADERS_ROLES, user_roles_ids))
        if not band_leader_role_id:
            await interaction.response.send_message(embed=nextcord.Embed(
                title=ERROR_HEADER,
                description=NOT_A_LEADER,
                color=nextcord.Color.red()
            ), ephemeral=True)
            return
        band_role = nextcord.utils.get(
            interaction.guild.roles,
            id=config.GROUP_ROLES[config.GROUP_LEADERS_ROLES.index(band_leader_role_id[0])])

        if action == "add":
            if band_role not in member.roles:
                await member.add_roles(band_role)
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=BAND_ROLE_SET,
                    description=f"Ковбой {member.mention} вступает в {band_role.mention}, и вместе с новыми "
                                f"товарищами готов взяться за дела, слава о которых "
                                f"еще прогремит по всему Дикому Западу!\n\n "                                
                                f"*Членство выдал предводитель банды {interaction.user.mention}*",
                    color=nextcord.Color.green()
                ))
                logging.info(f"Участник {member.display_name} получил членство в {band_role.name}, "
                             f"ee выдал предводитель банды {interaction.user.display_name}.")
            else:
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ERROR_HEADER,
                    description=f"Пользователь {member.mention} уже состоит в {band_role.mention}!",
                    color=nextcord.Color.red()
                ), ephemeral=True)
        elif action == "remove":
            if band_role in member.roles:
                await member.remove_roles(band_role)
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=BAND_ROLE_REMOVED,
                    description=f"Ковбой {member.mention} лишился членства в {band_role.mention}. Теперь он "
                                f"одиночка, которому никто не прикроет спину во время скитаний по прериям.\n\n "
                                f"*Членство отнял предводитель банды {interaction.user.mention}*",
                    color=nextcord.Color.green()
                ))
                logging.info(f"Участник {member.display_name} исключен из {band_role.name}, "
                             f"его выгнал предводитель банды {interaction.user.display_name}.")
            else:
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ERROR_HEADER,
                    description=f"Пользователя {member.mention} не является членом {band_role.mention}, "
                                f"выгонять его неоткуда!",
                    color=nextcord.Color.red()
                ), ephemeral=True)

    @band.subcommand(description="Добавить участника в свою банду")
    @application_checks.has_any_role(*config.GROUP_LEADERS_ROLES)
    async def add(
            self,
            interaction: nextcord.Interaction,
            member: nextcord.Member = nextcord.SlashOption(
                name="username",
                description="Имя пользователя, которому вы хотите дать членство в своей банде")
    ):
        await self.handle_role(interaction, member, action="add")

    @band.subcommand(description="Удалить участника из своей банды")
    @application_checks.has_any_role(*config.GROUP_LEADERS_ROLES)
    async def remove(
            self,
            interaction: nextcord.Interaction,
            member: nextcord.Member = nextcord.SlashOption(
                name="username",
                description="Имя пользователя, которого вы хотите исключить из своей банды")
    ):
        await self.handle_role(interaction, member, action="remove")


def setup(client):
    client.add_cog(BandManager(client))

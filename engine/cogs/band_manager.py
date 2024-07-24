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

    @nextcord.slash_command(description="Управление составом своей банды")
    @application_checks.has_any_role(*config.GROUP_LEADERS_ROLES)
    async def band(
            self,
            interaction: nextcord.Interaction,
            action: str = nextcord.SlashOption(
                name="action",
                description="Вы можете добавить пользователя в свою банду, либо исключить его",
                choices={"добавить в банду": "add", "исключить из банды": "remove"}
            ),
            member_to_assign: nextcord.Member = nextcord.SlashOption(
                name="username",
                description="Укажите имя пользователя"),
    ):
        if member_to_assign.bot:
            await interaction.response.send_message(embed=nextcord.Embed(
                title=ERROR_HEADER,
                description=UNABLE_TO_ASSIGN_ROLE_TO_BOT,
                color=nextcord.Color.red()
            ), ephemeral=True)
            return
        if member_to_assign.id == interaction.user.id:
            await interaction.response.send_message(embed=nextcord.Embed(
                title=ERROR_HEADER,
                description=UNABLE_TO_ASSIGN_ROLE_TO_YOURSELF,
                color=nextcord.Color.red()
            ), ephemeral=True)
            return

        band_leader_role_id = [role.id for role in interaction.user.roles if role.id in config.GROUP_LEADERS_ROLES]
        if not band_leader_role_id:
            await interaction.response.send_message(embed=nextcord.Embed(
                title=ERROR_HEADER,
                description=NOT_A_LEADER,
                color=nextcord.Color.red()
            ), ephemeral=True)
            return
        band_role_id = config.GROUP_ROLES[config.GROUP_LEADERS_ROLES.index(band_leader_role_id[0])]
        band_role = nextcord.utils.get(interaction.guild.roles, id=band_role_id)

        if action == "add":
            other_band_role_id = [
                role.id for role in member_to_assign.roles
                if role.id in (set(config.GROUP_ROLES) - {band_role_id})
            ]
            if other_band_role_id:
                other_band_role = nextcord.utils.get(interaction.guild.roles, id=other_band_role_id[0])
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ERROR_HEADER,
                    description=f"Вы не можете добавить пользователя {member_to_assign.mention} в свою банду, "
                                f"поскольку он уже состоит в {other_band_role.mention}!",
                    color=nextcord.Color.red()
                ), ephemeral=True)
                return

            if band_role not in member_to_assign.roles:
                await member_to_assign.add_roles(band_role)
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=BAND_ROLE_SET,
                    description=f"Ковбой {member_to_assign.mention} вступает в {band_role.mention}, и вместе с "
                                f"новыми товарищами готов взяться за дела, слава о которых "
                                f"еще прогремит по всему Дикому Западу!\n\n "
                                f"*Членство выдал предводитель банды {interaction.user.mention}*",
                    color=nextcord.Color.green()
                ))
                logging.info(f"Участник {member_to_assign.display_name} получил членство в {band_role.name}, "
                             f"ee выдал предводитель банды {interaction.user.display_name}.")
            else:
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ERROR_HEADER,
                    description=f"Пользователь {member_to_assign.mention} уже состоит в {band_role.mention}!",
                    color=nextcord.Color.red()
                ), ephemeral=True)
        elif action == "remove":
            if band_role in member_to_assign.roles:
                await member_to_assign.remove_roles(band_role)
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=BAND_ROLE_REMOVED,
                    description=f"Ковбой {member_to_assign.mention} лишился членства в {band_role.mention}. Теперь он "
                                f"одиночка, которому никто не прикроет спину во время скитаний по прериям.\n\n "
                                f"*Членство отнял предводитель банды {interaction.user.mention}*",
                    color=nextcord.Color.green()
                ))
                logging.info(f"Участник {member_to_assign.display_name} исключен из {band_role.name}, "
                             f"его выгнал предводитель банды {interaction.user.display_name}.")
            else:
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ERROR_HEADER,
                    description=f"Пользователя {member_to_assign.mention} не является членом {band_role.mention}, "
                                f"выгонять его неоткуда!",
                    color=nextcord.Color.red()
                ), ephemeral=True)


def setup(client):
    client.add_cog(BandManager(client))

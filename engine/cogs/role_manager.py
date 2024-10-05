import nextcord
from nextcord.ext import commands, application_checks
import logging
import engine.config as config

ERROR_HEADER = "Ошибка"
UNABLE_TO_ASSIGN_ROLE_TO_BOT = "Невозможно назначать или снимать роли у ботов!"
UNABLE_TO_ASSIGN_BAND_ROLE_TO_BOT = "Боты не могут находиться в банде."
UNABLE_TO_ASSIGN_ROLE_TO_YOURSELF = ("Предводитель банды всегда состоит в ней, "
                                     "и он не может быть удален или добавлен повторно.")
NOT_A_LEADER = "Вы не являетесь предводителем ни одной из банд."
ROLE_SET = "✅ Роль выдана"
BAND_ROLE_SET = "✅ Вступление в банду"
ROLE_REMOVED = "❌ Роль снята"
BAND_ROLE_REMOVED = "❌ Исключение из банды"


class RoleManager(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(description="Управление ролями соло сессии")
    @application_checks.has_any_role(config.ADMIN_ROLE, config.MODERATOR_ROLE, *config.GROUP_LEADERS_ROLES)
    async def solo(
            self,
            interaction: nextcord.Interaction,
            action: str = nextcord.SlashOption(
                name="action",
                description="Вы можете выдать пользователю роль соло сессии, либо снять ее с него",
                choices={"выдать роль": "add", "снять роль": "remove"}
            ),
            location: str = nextcord.SlashOption(
                name="location",
                description="Необходимо выбрать канал, для которого выдается или снимается разрешение",
                choices={"город Подфайловск": "city", "пригород Подфайловск": "suburb"}
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

        solo_role, solo_channel_name, solo_channel_link = None, None, None
        if location == "city":
            solo_role = nextcord.utils.get(interaction.guild.roles, id=config.SOLO_SESSION_ROLE)
            solo_channel_link = f"https://discord.com/channels/{config.GUILD_ID}/{config.SOLO_SESSION_CHANNEL}"
            solo_channel_name = "город Подфайловск"
        elif location == "suburb":
            solo_role = nextcord.utils.get(interaction.guild.roles, id=config.SOLO_SESSION_ROLE_SECOND)
            solo_channel_link = f"https://discord.com/channels/{config.GUILD_ID}/{config.SOLO_SESSION_CHANNEL_SECOND}"
            solo_channel_name = "пригород Подфайловска"
        if action == "add":
            if solo_role not in member_to_assign.roles:
                await member_to_assign.add_roles(solo_role)
                solo_role_assigned_embed = nextcord.Embed(
                    title=ROLE_SET,
                    description=f"Ковбой {member_to_assign.mention} получает роль {solo_role.mention} "
                                f"и въезжает в [{solo_channel_name}]({solo_channel_link})!\n\n "
                                f"*Роль выдал {interaction.user.mention}*",
                    color=nextcord.Color.green()
                )
                solo_role_assigned_image = nextcord.File(
                    config.SOLO_SESSION_IMAGE,
                    filename=config.SOLO_SESSION_IMAGE.split('/')[1]
                )
                solo_role_assigned_embed.set_image(url=f"attachment://{config.SOLO_SESSION_IMAGE.split('/')[1]}")
                await interaction.response.send_message(
                    embed=solo_role_assigned_embed,
                    file=solo_role_assigned_image
                )
                logging.info(f"Участник {member_to_assign.display_name} получил роль соло сессии "
                             f"(канал {solo_channel_name}), "
                             f"ee выдал модератор {interaction.user.display_name}.")
            else:
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ERROR_HEADER,
                    description=f"Пользователь {member_to_assign.mention} уже имеет роль {solo_role.mention}!",
                    color=nextcord.Color.red()
                ), ephemeral=True)
        elif action == "remove":
            if solo_role in member_to_assign.roles:
                await member_to_assign.remove_roles(solo_role)
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ROLE_REMOVED,
                    description=f"Ковбой {member_to_assign.mention} лишился роли {solo_role.mention} "
                                f"и покинул {solo_channel_name}.\n\n "
                                f"*Роль снял {interaction.user.mention}*",
                    color=nextcord.Color.green()
                ))
                logging.info(f"C участника {member_to_assign.display_name} снята роль соло сессии "
                             f"(канал {solo_channel_name}), "
                             f"ее забрал модератор {interaction.user.display_name}.")
            else:
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ERROR_HEADER,
                    description=f"У пользователя {member_to_assign.mention} нет роли {solo_role.mention}, "
                                f"снимать с него нечего!",
                    color=nextcord.Color.red()
                ), ephemeral=True)

    @nextcord.slash_command(description="Управление ролью участника ивента")
    @application_checks.has_any_role(config.ADMIN_ROLE, config.MODERATOR_ROLE, *config.GROUP_LEADERS_ROLES)
    async def event(
            self,
            interaction: nextcord.Interaction,
            action: str = nextcord.SlashOption(
                name="action",
                description="Вы можете выдать пользователю роль участника ивента, либо снять ее с него",
                choices={"выдать роль": "add", "снять роль": "remove"}
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

        event_role = nextcord.utils.get(interaction.guild.roles, id=config.SOLO_EVENT_ROLE)
        if action == "add":
            if event_role not in member_to_assign.roles:
                await member_to_assign.add_roles(event_role)
                event_role_assigned_embed = nextcord.Embed(
                    title=ROLE_SET,
                    description=f"Ковбой {member_to_assign.mention} получает роль {event_role.mention} и ему "
                                f"открывается доступ в канал <#{config.SOLO_EVENT_CHANNEL}>.\n Теперь ему доведется "
                                f"пережить невероятные и безумные приключения, что запомнятся на долгие годы!\n\n "
                                f"*Роль выдал {interaction.user.mention}*",
                    color=nextcord.Color.green()
                )
                event_role_assigned_image = nextcord.File(
                    config.SOLO_EVENT_IMAGE,
                    filename=config.SOLO_EVENT_IMAGE.split('/')[1]
                )
                event_role_assigned_embed.set_image(url=f"attachment://{config.SOLO_EVENT_IMAGE.split('/')[1]}")
                await interaction.response.send_message(
                    embed=event_role_assigned_embed,
                    file=event_role_assigned_image
                )
                logging.info(f"Участник {member_to_assign.display_name} получил роль участника ивента, "
                             f"ee выдал модератор {interaction.user.display_name}.")
            else:
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ERROR_HEADER,
                    description=f"Пользователь {member_to_assign.mention} уже имеет роль {event_role.mention}!",
                    color=nextcord.Color.red()
                ), ephemeral=True)
        elif action == "remove":
            if event_role in member_to_assign.roles:
                await member_to_assign.remove_roles(event_role)
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ROLE_REMOVED,
                    description=f"Ковбой {member_to_assign.mention} лишился роли {event_role.mention} "
                                f"и завершил участие в ивенте. Организаторы надеются, что ему было весело!\n\n "
                                f"*Роль снял {interaction.user.mention}*",
                    color=nextcord.Color.green()
                ))
                logging.info(f"C участника {member_to_assign.display_name} снята роль участника ивента, "
                             f"ее забрал модератор {interaction.user.display_name}.")
            else:
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ERROR_HEADER,
                    description=f"У пользователя {member_to_assign.mention} нет роли {event_role.mention}, "
                                f"снимать с него нечего!",
                    color=nextcord.Color.red()
                ), ephemeral=True)

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
                description=UNABLE_TO_ASSIGN_BAND_ROLE_TO_BOT,
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
                                f"поскольку он уже состоит в {other_band_role.mention}! Нельзя состоять более, чем "
                                f"в одной банде.",
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
    client.add_cog(RoleManager(client))

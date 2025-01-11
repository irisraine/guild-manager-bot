import nextcord
from nextcord.ext import commands, application_checks
import logging
import engine.config as config
import engine.messages as messages


class RoleManager(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(description="Управление ролями соло сессии")
    @application_checks.has_any_role(config.ADMIN_ROLE, config.MODERATOR_ROLE, config.MODERATOR_ASSISTANT_ROLE)
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
            return await interaction.response.send_message(
                **messages.error(description="Невозможно назначать или снимать роли у ботов!"))
        solo_role = nextcord.utils.get(interaction.guild.roles, id=config.SOLO_SESSION[location]['role'])
        solo_channel_link = f"https://discord.com/channels/{config.GUILD_ID}/{config.SOLO_SESSION[location]['channel']}"
        solo_channel_name = config.SOLO_SESSION[location]['name']
        if action == "add":
            if solo_role not in member_to_assign.roles:
                await member_to_assign.add_roles(solo_role)
                await interaction.response.send_message(
                    **messages.custom_embed(
                        title="✅ Роль выдана",
                        description=f"Ковбой {member_to_assign.mention} получает роль {solo_role.mention} и "
                                    f"въезжает в [{solo_channel_name}]({solo_channel_link})!\n\n "
                                    f"*Роль выдал {interaction.user.mention}*",
                        image_path=config.SOLO_SESSION_IMAGE)
                )
                logging.info(f"Участник {member_to_assign.display_name} получил роль соло сессии "
                             f"(канал {solo_channel_name}), "
                             f"ee выдал модератор {interaction.user.display_name}.")
            else:
                return await interaction.response.send_message(
                    **messages.error(description=f"Пользователь {member_to_assign.mention} уже имеет "
                                                 f"роль {solo_role.mention}!"))
        elif action == "remove":
            if solo_role in member_to_assign.roles:
                await member_to_assign.remove_roles(solo_role)
                await interaction.response.send_message(
                    **messages.custom_embed(
                        title="❌ Роль снята",
                        description=f"Ковбой {member_to_assign.mention} лишился роли {solo_role.mention} и "
                                    f"покинул {solo_channel_name}.\n\n "
                                    f"*Роль снял {interaction.user.mention}*",
                        image_path=config.SOLO_SESSION_LEFT_OFF_IMAGE),
                )
                logging.info(f"C участника {member_to_assign.display_name} снята роль соло сессии "
                             f"(канал {solo_channel_name}), "
                             f"ее забрал модератор {interaction.user.display_name}.")
            else:
                return await interaction.response.send_message(
                    **messages.error(description=f"У пользователя {member_to_assign.mention} нет "
                                                 f"роли {solo_role.mention}, снимать с него нечего!"))

    @nextcord.slash_command(description="Управление ролью участника ивента")
    @application_checks.has_any_role(config.ADMIN_ROLE, config.MODERATOR_ROLE, config.MODERATOR_ASSISTANT_ROLE, *config.AUTHORIZED_BAND_LEADERS_ROLES)
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
            return await interaction.response.send_message(
                **messages.error(description="Невозможно назначать или снимать роли у ботов!"))
        event_role = nextcord.utils.get(interaction.guild.roles, id=config.SOLO_EVENT['role'])
        if action == "add":
            if event_role not in member_to_assign.roles:
                await member_to_assign.add_roles(event_role)
                await interaction.response.send_message(
                    **messages.custom_embed(
                        title="✅ Роль выдана",
                        description=f"Ковбой {member_to_assign.mention} получает роль {event_role.mention} и "
                                    f"ему открывается доступ в канал <#{config.SOLO_EVENT['channel']}>.\n "
                                    f"Теперь ему доведется пережить невероятные и безумные приключения, "
                                    f"что запомнятся на долгие годы!\n\n *Роль выдал {interaction.user.mention}*",
                        image_path=config.SOLO_EVENT_IMAGE)
                )
                logging.info(f"Участник {member_to_assign.display_name} получил роль участника ивента, "
                             f"ee выдал модератор {interaction.user.display_name}.")
            else:
                return await interaction.response.send_message(
                    **messages.error(description=f"Пользователь {member_to_assign.mention} уже имеет "
                                                 f"роль {event_role.mention}!"))
        elif action == "remove":
            if event_role in member_to_assign.roles:
                await member_to_assign.remove_roles(event_role)
                await interaction.response.send_message(
                    **messages.custom_embed(
                        title="❌ Роль снята",
                        description=f"Ковбой {member_to_assign.mention} лишился роли {event_role.mention} и завершил "
                                    f"участие в ивенте. Несомненно, впечатлений ему хватит на целую жизнь!\n\n "
                                    f"*Роль снял {interaction.user.mention}*",
                        image_path=config.SOLO_EVENT_LEFT_OFF_IMAGE),
                )
                logging.info(f"C участника {member_to_assign.display_name} снята роль участника ивента, "
                             f"ее забрал модератор {interaction.user.display_name}.")
            else:
                return await interaction.response.send_message(
                    **messages.error(description=f"У пользователя {member_to_assign.mention} нет "
                                                 f"роли {event_role.mention}, снимать с него нечего!"))

    @nextcord.slash_command(description="Управление составом своей банды")
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
        band_leader_role_id = [role.id for role in interaction.user.roles if role.id in config.AUTHORIZED_BAND_LEADERS_ROLES]
        if not band_leader_role_id:
            return await interaction.response.send_message(
                **messages.error(description="Вы не являетесь предводителем ни одной из банд и не можете выдавать "
                                             "бандитскую роль участникам."))
        if member_to_assign.bot:
            return await interaction.response.send_message(
                **messages.error(description="Боты не могут находиться в банде."))
        if member_to_assign.id == interaction.user.id:
            return await interaction.response.send_message(
                **messages.error(description="Предводитель банды всегда состоит в ней, и он не может быть "
                                             "удален или добавлен повторно."))
        band_role_id = config.AUTHORIZED_BAND_ROLES[config.AUTHORIZED_BAND_LEADERS_ROLES.index(band_leader_role_id[0])]
        band_role = nextcord.utils.get(interaction.guild.roles, id=band_role_id)

        if action == "add":
            other_band_role_id = [
                role.id for role in member_to_assign.roles
                if role.id in (set(config.AUTHORIZED_BAND_ROLES) - {band_role_id})
            ]
            if other_band_role_id:
                other_band_role = nextcord.utils.get(interaction.guild.roles, id=other_band_role_id[0])
                return await interaction.response.send_message(
                    **messages.error(description=f"Вы не можете добавить пользователя {member_to_assign.mention} "
                                                 f"в свою банду, поскольку он уже состоит в {other_band_role.mention}! "
                                                 f"Нельзя состоять более, чем в одной банде."))
            if band_role not in member_to_assign.roles:
                await member_to_assign.add_roles(band_role)
                await interaction.response.send_message(
                    **messages.custom_embed(
                        title="✅ Вступление в банду",
                        description=f"Ковбой {member_to_assign.mention} вступает в {band_role.mention}, и вместе с "
                                    f"новыми товарищами готов взяться за дела, слава о которых еще прогремит по всему "
                                    f"Дикому Западу!\n\n *Членство выдал предводитель банды {interaction.user.mention}*",
                        image_path=config.BAND_IMAGE)
                )
                logging.info(f"Участник {member_to_assign.display_name} получил членство в '{band_role.name}', "
                             f"ee выдал предводитель банды {interaction.user.display_name}.")
            else:
                return await interaction.response.send_message(
                    **messages.error(description=f"Пользователь {member_to_assign.mention} уже состоит "
                                                 f"в {band_role.mention}!"))
        elif action == "remove":
            if band_role in member_to_assign.roles:
                await member_to_assign.remove_roles(band_role)
                await interaction.response.send_message(
                    **messages.custom_embed(
                        title="❌ Исключение из банды",
                        description=f"Ковбой {member_to_assign.mention} лишился членства в {band_role.mention}. Теперь "
                                    f"он одиночка, которому никто не прикроет спину во время скитаний по прериям.\n\n "
                                    f"*Членство отнял предводитель банды {interaction.user.mention}*",
                        image_path=config.BAND_LEFT_OFF_IMAGE),
                )
                logging.info(f"Участник {member_to_assign.display_name} исключен из '{band_role.name}', "
                             f"его выгнал предводитель банды {interaction.user.display_name}.")
            else:
                return await interaction.response.send_message(
                    **messages.error(description=f"Пользователя {member_to_assign.mention} не является "
                                                 f"членом {band_role.mention}, выгонять его неоткуда!"))


def setup(client):
    client.add_cog(RoleManager(client))

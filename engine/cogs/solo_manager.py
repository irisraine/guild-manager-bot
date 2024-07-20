import nextcord
from nextcord.ext import commands
import logging
import engine.config as config


class SoloToggler(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def solo(self, ctx, username: str):
        if not (ctx.author.guild_permissions.administrator or
                any(role.id in [config.MODERATOR_ROLE_ID] + config.GROUP_LEADERS_ROLES for role in ctx.author.roles)):
            await ctx.send(embed=nextcord.Embed(
                title="Ошибка!",
                description="Выдавать гражданство славного города Подфайловска "
                            "могут только админы, маршалы и предводители банд!",
                color=nextcord.Color.red()
            ))
            return

        member = nextcord.utils.get(ctx.guild.members, name=username)
        role = nextcord.utils.get(ctx.guild.roles, id=config.SOLO_SESSION_ROLE)
        if not member:
            await ctx.send(embed=nextcord.Embed(
                title="Ошибка!",
                description=f"Пользователь с именем {username} не присутствует на сервере.",
                color=nextcord.Color.red()
            ))
            return

        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(embed=nextcord.Embed(
                title="❌ Роль снята",
                description=f"Ковбой {member.mention} лишился роли {role.mention}, а вместе с ней и гражданства "
                            f"города Подфайловска, и был вынужден покинуть его.\n\n "
                            f"*Роль снял {ctx.author.mention}*",
                color=nextcord.Color.green()
            ))
            logging.info(f"C участника {username} снята роль соло сессии, "
                         f"ее забрал модератор {ctx.author.display_name}.")
        else:
            await member.add_roles(role)
            await ctx.send(embed=nextcord.Embed(
                title="✅ Роль выдана",
                description=f"Ковбой {member.mention} получает роль {role.mention} "
                            f"и триумфально въезжает в город Подфайловск, становясь его полноправным гражданином!\n\n "
                            f"*Роль выдал {ctx.author.mention}*",
                color=nextcord.Color.green()
            ))
            logging.info(f"Участник {username} получил роль соло сессии, "
                         f"ee выдал модератор {ctx.author.display_name}.")


def setup(client):
    client.add_cog(SoloToggler(client))

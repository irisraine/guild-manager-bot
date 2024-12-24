import nextcord
from nextcord.ext import commands, tasks, application_checks
from PIL import Image, ImageDraw, ImageFont
import logging
import engine.config as config
import engine.messages as messages


class BannerTask(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.member_counter = {
            'members': 0,
            'voice': 0
        }

    @staticmethod
    def update_banner(members_count, voice_count):
        members_count, voice_count = str(members_count), str(voice_count)
        banner = Image.open(config.BANNER_IMAGE)
        counter_overlay = Image.open(config.COUNTER_OVERLAY_IMAGE)
        banner = banner.convert("RGBA")
        banner_width, banner_height = banner.size
        counter_overlay_width, counter_overlay_height = counter_overlay.size

        x_shift_overlay = banner_width - counter_overlay_width - 15
        y_shift_overlay = int(banner_height / 2)

        banner.paste(counter_overlay, (x_shift_overlay, y_shift_overlay), counter_overlay)
        banner_with_counter = banner.convert("RGB")
        draw = ImageDraw.Draw(banner_with_counter)
        font = ImageFont.truetype(config.CUSTOM_RDO_FONT, size=80)
        members_count_text_length = int(draw.textlength(members_count, font))
        voice_count_text_length = int(draw.textlength(voice_count, font))

        x_shift_text_users, y_shift_text_users = (banner_width - members_count_text_length - 30), y_shift_overlay + 5
        x_shift_text_voice, y_shift_text_voice = (banner_width - voice_count_text_length - 30), y_shift_overlay + 110

        draw.text((x_shift_text_users, y_shift_text_users), members_count, fill='white', font=font)
        draw.text((x_shift_text_voice, y_shift_text_voice), voice_count, fill='white', font=font)
        banner_with_counter.save(config.BANNER_WITH_COUNTER_IMAGE)

    @staticmethod
    def get_banner_binary_data(image):
        with open(image, 'rb') as banner_file:
            banner_binary_data = banner_file.read()
        return banner_binary_data

    @tasks.loop(minutes=10)
    async def banner_member_counter(self):
        guild = self.client.get_guild(config.GUILD_ID)
        current_members_count = guild.member_count
        current_voice_count = sum(1 for member in guild.members if member.voice)

        if current_members_count != self.member_counter['members'] or current_voice_count != self.member_counter['voice']:
            self.update_banner(
                members_count=current_members_count,
                voice_count=current_voice_count
            )
            banner_binary_data = self.get_banner_binary_data(config.BANNER_WITH_COUNTER_IMAGE)
            await guild.edit(banner=banner_binary_data)
            self.member_counter = {
                'members': current_members_count,
                'voice': current_voice_count
            }

    @nextcord.slash_command(description="Управление динамическим баннером сервера")
    @application_checks.has_role(config.ADMIN_ROLE)
    async def dynamic_banner(
            self,
            interaction: nextcord.Interaction,
            toggle: str = nextcord.SlashOption(
                description="Отображение динамического баннера",
                choices={"активировать": "on", "отключить": "off"}
            )):
        if toggle == "on":
            if not self.banner_member_counter.is_running():
                self.banner_member_counter.start()
        elif toggle == "off":
            self.banner_member_counter.stop()
            guild = self.client.get_guild(config.GUILD_ID)
            banner_binary_data = self.get_banner_binary_data(config.BANNER_IMAGE)
            await guild.edit(banner=banner_binary_data)
        status = "активирован" if toggle == "on" else "отключен"
        await interaction.response.send_message(**messages.custom_embed_message(
            description=f"Динамический баннер {status}.",
            color="red"
        ))
        logging.info(f"Динамический баннер {status}.")


def setup(client):
    client.add_cog(BannerTask(client))

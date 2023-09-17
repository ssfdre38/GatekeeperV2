
import psutil
import sys

import discord
from discord import Embed, Interaction

from DB import DBHandler
from Gatekeeper import Gatekeeper
from utils.utils import count_lines, count_others


def default_embedmsg(title, interaction: Interaction, description=None, field=None, field_value=None) -> Embed:
    """This Embed has only one Field Entry."""
    embed = Embed(title=title, description=description, color=0x808000)  # color is RED
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar)
    embed.add_field(name=field, value=field_value, inline=False)
    return embed


def bot_settings_embed(interaction: Interaction) -> Embed:
    """Default Embed Reply for command /bot settings, please pass in a List of Dictionaries eg {'setting_name': 'value'}"""
    _db_handler: DBHandler = DBHandler()
    _db_config = _db_handler._DBConfig
    embed = Embed(title=f'**Bot Settings**', color=0x71368a)
    embed.set_thumbnail(url=interaction.guild.icon)
    embed.add_field(name='\u1CBC\u1CBC', value='\u1CBC\u1CBC', inline=False)

    # This allows me to control which settings display first.
    layout = ["bot_version",
              "db_version",
              # "guild_id",
              "moderator_role_id",
              "permissions",
              "message_timeout",
              "banner_type",
              "banner_auto_update",
              "auto_whitelist",
              "whitelist_wait_time",
              "whitelist_request_channel",
              "donator_role_id",
              "donator_bypass"]

    # Take our list and store it in a seperate list and lowercase the strings.
    db_config_settingslist = [x.lower() for x in _db_config.GetSettingList()]
    for key in layout:
        # If the key is not in the DB; skip.
        if key not in db_config_settingslist:
            continue

        db_config_settingslist.remove(key)
        value = _db_config.GetSetting(key)
        key = key.lower()
        if key == 'auto_whitelist':
            embed.add_field(name='Auto Whitelisting:', value=f'{"True" if value == 1 else "False"}')

        elif key == 'whitelist_wait_time':
            embed.add_field(name='Whitelist Wait Time:', value=f'{"Instantly" if value == 0 else (str(value) + " Minutes")} ', inline=False)

        elif key == 'whitelist_request_channel':
            if value != 'None':
                value = interaction.guild.get_channel(value)

            embed.add_field(name='Whitelist Request Channel:', value=f'{value.name.title() if value != None else "Not Set"}', inline=False)

        elif key == 'message_timeout':
            embed.add_field(name='Gatekeeper Reply Timeout', value=f'{value} Seconds', inline=False)

        elif key == 'permissions':
            if value == 0:
                value = 'Default'
            elif value == 1:
                value = 'Custom'
            embed.add_field(name='Permissions:', value=f'{value}', inline=True)

        elif key == 'banner_type':
            if value == 0:
                value = 'Discord Embeds'
            elif value == 1:
                value = 'Custom Banner Images'
            embed.add_field(name='Banner Type:', value=f'{value}', inline=False)

        elif key == 'banner_auto_update':
            embed.add_field(name='Banner Auto Update:', value=f'{"True" if value == 1 else "False"}', inline=True)

        elif key == 'db_version':
            embed.add_field(name='Database Version:', value=f'{value}', inline=True)

        elif key == 'bot_version':
            embed.add_field(name='Gatekeeper Version:', value=f'{value}', inline=True)

        # elif key == 'guild_id':
        #     if self._client != None and value != 'None':
        #         value = interaction..get_guild(value)

        #         embed.add_field(name='Guild ID:', value=f'{value.name.title() if value != None else "Not Set"}', inline=False)

        elif key == 'moderator_role_id':
            if value != 'None':
                value = interaction.guild.get_role(value)

            embed.add_field(name='Moderator Role:', value=f'{value.name.title() if value != None else "Not Set"}', inline=True)

        elif key == "donator_role_id":
            if value != 'None':
                value = interaction.guild.get_role(value)

            embed.add_field(name='Donator Role ID:', value=f'{value.name.title() if value != None else "Not Set"}', inline=True)

        elif key == 'donator_bypass':
            embed.add_field(name='Donator Bypass:', value=f'{"True" if value == 1 else "False"}', inline=True)

    # This iterates through the remaining keys of the Settings List and adds them to the Embed.
    for key in db_config_settingslist:
        value = _db_config.GetSetting(key)
        key = key.replace("_", " ").title()  # Turns `auto_whitelist`` into `Auto Whitelist`

        # For our possible bool entries (0, 1) to True and False respectively.
        if type(value) == int:
            embed.add_field(name=key, value=f'{"False" if value == 0 else "True"}', inline=False)
        else:
            embed.add_field(name=key, value=value, inline=False)

        embed.set_footer(text=f"Need help? Visit Kat's Paradise https://discord.gg/BtNyU8DFtt")
    return embed


async def bot_about_embed(client: Gatekeeper) -> Embed:
    """Discord Bot Detailed Information Embed"""
    # information = await self._client.application_info()
    owner = client.get_user(144462063920611328)
    embed = Embed(color=0x71368a)
    #embed.add_field(name="Latest updates:", value=get_latest_commits(limit=5), inline=False)

    embed.set_author(name=f"Made by {owner.name}", icon_url=owner.display_avatar.url)
    embed.add_field(name="Gatekeeper Version", value=client._version)
    memory_usage = psutil.Process().memory_full_info().uss / 1024**2
    cpu_usage = psutil.cpu_percent()
    embed.add_field(name="Discord Version", value=discord.__version__)
    embed.add_field(name="System/Python Version", value=sys.version)
    embed.add_field(name="SQL DB Version", value=client._DBHandler._DB_Version)
    embed.add_field(name="SQL DB Exists", value=client._DBHandler._SuccessfulDatabase)
    # FIXME -- This may return; unsure if I want to make it apart of the main bot or a cog.
    #embed.add_field(name="AMP Connectected", value=client._AMPHandler.SuccessfulConnection)
    embed.add_field(name="Process", value=f"{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU")
    embed.add_field(name="Uptime", value=f"{client._uptime}")

    try:
        embed.add_field(
            name="Lines",
            value=f"Lines: {await count_lines('./', '.py'):,}"
            f"\nFunctions: {await count_others('./', '.py', 'def '):,}"
            f"\nClasses: {await count_others('./', '.py', 'class '):,}",
        )
    except (FileNotFoundError, UnicodeDecodeError):
        pass

    embed.set_footer(
        text=f"Made with discord.py v{discord.__version__}",
        icon_url="https://i.imgur.com/5BFecvA.png",
    )
    embed.timestamp = discord.utils.utcnow()
    return embed
from discord.ext import commands
import discord
from models import GuildConfig, WelcomeConfig, LeaveConfig, Members


class Events(commands.Cog):
    def __int__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        new_config = GuildConfig(id=guild.id)
        await new_config.save()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        config = await GuildConfig.filter(id=member.guild.id).get_or_none()
        new_member = Members(member_id=member.id, identity=member)
        await new_member.save()
        if not config:
            return

        if config.welcome_enabled:
            welcome_config = await WelcomeConfig.filter(guild_id=member.guild.id).get_or_none()
            embed = discord.Embed(title="Welcome!", color=discord.Colour.blue())
            embed.set_image(url=member.avatar_url)
            embed.description = welcome_config.message.format(member.mention)

            send_channel = discord.utils.get(member.guild.channels, id=welcome_config.channel_id)
            await send_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        config = await GuildConfig.filter(id=member.guild.id).get_or_none()
        if not config:
            return

        if config.leave_enabled:
            leave_config = await LeaveConfig.filter(guild_id=member.guild.id).get_or_none()
            embed = discord.Embed(title="Member left", color=discord.Colour.blue())
            embed.set_image(url=member.avatar_url)
            embed.description = leave_config.message.format(member.mention)

            send_channel = discord.utils.get(member.guild.channels, id=leave_config.channel_id)
            await send_channel.send(embed=embed)


def setup(client):
    client.add_cog(Events(client))
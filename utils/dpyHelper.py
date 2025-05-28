import re
import asyncio
import discord
from discord.ext import commands,tasks
from dateutil.relativedelta import relativedelta
from typing import Union, List, Optional
from dateutil.relativedelta import relativedelta

time_regex = re.compile(r"(( ?(\d{1,5})(h|s|m|d))+)")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class dpyhelp():
     #GetORFetch
     async def get_or_fetch_channel(bot, guild: discord.Guild, channel_id: int) -> Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel]:
          channel = guild.get_channel(channel_id)
          if channel == None:
               channel = await bot.fetch_channel(channel_id)
          
          return channel

     async def get_or_fetch_member(guild: discord.Guild, member_id: int) -> discord.Member:
          member = guild.get_member(member_id)
          if not member:
               member = await guild.fetch_member(member_id)
          return member

     
     #Prompts
     async def GetMessage(
        bot, ctx, contentOne="Default Message", contentTwo="\uFEFF", timeout=100
     ):
        """
        This function sends an embed containing the params and then waits for a message to return
        Params:
        - bot (commands.Bot object) :
        - ctx (context object) : Used for sending msgs n stuff
        - Optional Params:
            - contentOne (string) : Embed title
            - contentTwo (string) : Embed description
            - timeout (int) : Timeout for wait_for
        Returns:
        - msg.content (string) : If a message is detected, the content will be returned
        or
        - False (bool) : If a timeout occurs
        """
        embed = discord.Embed(
            title=f"{contentOne}",
            description=f"{contentTwo}",
        )
        sent = await ctx.send(embed=embed)
        try:
            msg = await bot.wait_for(
                "message",
                timeout=timeout,
                check=lambda message: message.author == ctx.author
                and message.channel == ctx.channel,
            )
            if msg:
                return msg.content
        except asyncio.TimeoutError:
            return False


     async def get_input(
        ctx,
        title: str = None,
        description: str = None,
        *,
        timeout: int = 100,
        delete_after: bool = False,
        author_id=None,
     ):
        if title and not description:
            embed = discord.Embed(
                title=title,
            )
        elif not title and description:
            embed = discord.Embed(
                description=description,
            )
        elif title and description:
            embed = discord.Embed(
                title=title,
                description=description,
            )
        else:
            raise RuntimeError("Expected atleast title or description")

        sent = await ctx.send(embed=embed)
        val = None

        author_id = author_id or ctx.author.id or ctx.id  # or self.id for User/Member

        try:
            msg = await ctx.bot.wait_for(
                "message",
                timeout=timeout,
                check=lambda message: message.author.id == author_id,
            )
            if msg:
                val = msg.content
        except asyncio.TimeoutError:
            if delete_after:
                await sent.delete()

            return val

        try:
            if delete_after:
                await sent.delete()
                await msg.delete()
        finally:
            return val


     #Time
     async def time_convertor(argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        if not matches:
            return 0

        matches = matches[0][0].split(" ")
        matches = [filter(None, re.split(r"(\d+)", s)) for s in matches]
        time = 0
        for match in matches:
            key, value = match
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return time






 
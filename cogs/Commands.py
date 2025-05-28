import discord
from typing import Union
from discord.ext import commands

from cogs.TButtons import *
from utils.util import utilmisc 
from TicketManagement.TicketActions import TicketActions
from db import ticket_db

class StaffCommands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print(f"{self.__class__.__name__} Cog has been loaded\n-----")

  @commands.command() 
  @commands.guild_only()
  async def close(self,ctx):
    await TicketActions.close_ticket(self,ctx.guild,ctx.author,ctx.channel,"c")

  #Delete
  @commands.command(aliases=["del"]) 
  @commands.guild_only()
  async def delete(self,ctx):
    await TicketActions.delete_ticket(self,ctx.guild,ctx.author,ctx.channel,"c")    

  @commands.command() 
  @commands.guild_only()
  async def add(self, ctx: commands.Context, target: Union[discord.Member, discord.Role]):
    tchannel = await ticket_db.find_by_custom({"channelid":ctx.channel.id})
    StaffList = await utilmisc.build_stafflist(self)
    if ctx.author.id not in StaffList:
      return  await ctx.send("> **Error** : You do not have permission to do that")

    if not tchannel:
      return  await ctx.send("> **Error** : This is not a ticket?")

    await ctx.message.delete()
    await ctx.channel.set_permissions(target, view_channel=True,send_messages=True,read_message_history=True,embed_links=True,attach_files=True)
    await ctx.send(embed=discord.Embed(description=f"{target.mention} added to ticket <#{ctx.channel.id}>",colour=0x00FF27))


  @add.error
  async def add_error(self,ctx, error):
    if isinstance(error, commands.BadUnionArgument):
      await ctx.send("> **Error** : You didnt mention a User/Role")

  @commands.command() 
  @commands.guild_only()
  async def remove(self, ctx: commands.Context, target: Union[discord.Member, discord.Role]):
    tchannel = await ticket_db.find_by_custom({"channelid":ctx.channel.id})
    StaffList = await utilmisc.build_stafflist(self)
    if ctx.author.id not in StaffList:
      return await ctx.send("> **Error** : You do not have permission to do that")
    
    if not tchannel:
      return await ctx.send("> **Error** : This is not a ticket?")
  
    await ctx.message.delete()
    await ctx.channel.set_permissions(target, view_channel=False,send_messages=False,read_message_history=False)
    await ctx.send(embed=discord.Embed(description=f"{target.mention} removed from ticket <#{ctx.channel.id}>",colour=0x00FF27))

  @remove.error
  async def remove_error(self,ctx, error):
    if isinstance(error, commands.BadUnionArgument):
      await ctx.send("> **Error** : You didnt mention a User/Role")


  @commands.command() 
  @commands.cooldown(1, 600, commands.BucketType.guild)
  @commands.guild_only()
  async def rename(self, ctx,*, name):
    await TicketActions.rename_ticket_channel(self,ctx.author,ctx.message,ctx.channel,name)

  @rename.error
  async def rename_error(self,ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.send(f"> **Warning:** Channel being renamed too quickly, Timeout: {round(error.retry_after, 2)}")
    else:
      raise error



async def setup(bot):
  await bot.add_cog(StaffCommands(bot))





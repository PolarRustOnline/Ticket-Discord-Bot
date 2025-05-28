import json
from pydoc import cli
import discord
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from discord.ext import commands,tasks
import asyncio
from threading import Thread
from utils.mongo import Document
import uvicorn
from fastapi import  FastAPI,APIRouter,HTTPException
from cogs.Create import Creation
from utils.json import *

import logging
logging.basicConfig(level=logging.INFO)

client = commands.Bot(command_prefix="$", intents=discord.Intents.all(),case_insensitive=True)
client.remove_command("help")

with open("Configuration/config.json", "r") as f:
    client.data = json.load(f)
    client.embed_hex = int(client.data["Hex_Color"].replace("#", "0x"), 16)

with open("Configuration/questions.json", "r") as f:
    client.questions_data = json.load(f)   

@client.event
async def on_ready():
    print("we have logged in as {0.user}".format(client))


@client.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return
        
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please pass in all required arguments")

    elif isinstance(error , commands.CommandNotFound):
        return
    
    elif isinstance(error , commands.NoPrivateMessage):
        return

    elif isinstance(error, commands.errors.MissingAnyRole):
        await ctx.channel.purge(limit=1)
        await ctx.send(f"{ctx.author.mention}, You don't have perms for this command ")

    else:
      raise error

@client.command(aliases=["h"])
async def help(ctx):    
    embed = discord.Embed(title = "Ticket Commands",description=f"Using Prefix `{ctx.prefix}`",color = client.embed_hex)
    embed.add_field(
        name="Staff",
        value = f"> **{ctx.prefix}close** - Close a ticket\n"
        f"> **{ctx.prefix}delete** - Delete a ticket\n"
        f"> **{ctx.prefix}add** *@user/role* - Adds a User / Role to the ticket\n"
        f"> **{ctx.prefix}remove** *@user/role* - Removes a User / Role to the ticket\n"
        f"> **{ctx.prefix}close** *msg* - Close a ticket\n"
        f"> **{ctx.prefix}rename** *newname* - Changes the channel name\n"
        f"> **{ctx.prefix}msguser** *message* - Sends a msg to a user\n"
        ,
        inline=False
    )

    embed.set_footer(text=client.data["Footer"],icon_url=client.data["Main_thumbnail_url"])
    await ctx.send(embed=embed)


extensions = [
  "cogs.Commands",
  "cogs.Create",
  "cogs.TButtons"
]

#Start the actual bot
async def main():
    for ext in extensions:
        await client.load_extension(ext)

    async with client:
        await client.start(client.data["BOT_TOKEN"],reconnect=True)
asyncio.run(main())

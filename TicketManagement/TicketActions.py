import discord
import asyncio
from typing import Union
from discord.ext import commands
import chat_exporter
import io
from datetime import datetime
 
#import ReOpenButtons
import cogs.TButtons as TButtons
from utils.util import utilmisc 
from db import ticket_db

#This should realistically be a ticket object class - potentially to be done in the future (written in 2021 0.o) 
#hello in 2024 still haven't got round to this oops 

class TicketActions():
     async def generate_transcript_link(
          self,
          channel: discord.TextChannel,
          guild: discord.Guild
          ) -> str:
          """
          Generate a transcript a ticket and produce a discord hosted .html file
          """
          #FetchLoggingChannel
          loggingchan = guild.get_channel(self.bot.data["File_Log_Channel_ID"])
          transcript = await chat_exporter.export(
               channel,
               limit=1000,
               bot=self.bot,
          )
          if not transcript:
               return "None"
          transcript_file = discord.File(io.BytesIO(transcript.encode()),filename=f"transcript-{channel.name}.html")

          #SendFile&GenerateDiscordHostedLink
          filemsg = await loggingchan.send(file=transcript_file)
          attachments = filemsg.attachments
          link = attachments[0].url

          return link

     async def transcript_embed(
          self,
          channel: discord.TextChannel,
          link: str,
          tchannel: dict,
          member: discord.Member,
          category: str
          ) -> discord.Embed:
          """
          Generate an embed with all the relavent transcript info
          """
          towner_id = tchannel["member_id"]
          towner_name = tchannel["member_name"]
          closeembed=discord.Embed(title="Ticket Closed",colour=self.bot.embed_hex,timestamp=datetime.now())
          closeembed.set_thumbnail(url=self.bot.data["Main_thumbnail_url"])
          closeembed.set_author(name=f"{towner_name} | {towner_id}")
          closeembed.add_field(name="Direct Transcript",value=f"[Direct Transcript]({link})",inline=False)
          closeembed.add_field(name="Closed By",value=member.mention,inline=True)
          closeembed.add_field(name="Ticket Name",value=channel,inline=True)
          closeembed.add_field(name="Category",value=category,inline=True)
          closeembed.set_footer(text=self.bot.data["Footer"])


          return closeembed

 
     async def pick_channel(
          self,
          guild: discord.Guild,
          category: str
          )-> discord.TextChannel:
          """
          Take in a ticket category and reuturn the correct logging channel
          """
          if category not in self.bot.questions_data["Categories"]:
               return None
          
          ticket_type_info = self.bot.questions_data["Categories"][category]
          channel = guild.get_channel(ticket_type_info["Log_Channel_ID"])
          return channel


     async def close_ticket(
          self,
          guild: discord.Guild,
          action_author: discord.Member,
          ctx_channel: discord.TextChannel,
          interaction_or_channel: str,
          interaction : discord.Interaction = None
          ) -> None:
          """
          Quickly close a ticket from a command / interaction allowing for the ability to send a transcript to the user if desired
          """

          #CheckItsStaff
          #StaffList = await utilmisc.build_stafflist(self)
          #if action_author.id not in StaffList:
          #     if interaction_or_channel == "i":
           #         return await interaction.response.send_message(content="> **Error** : You do not have permission to do that",ephemeral=True)
               
            #   elif interaction_or_channel == "c":
            #        return await ctx_channel.send("> **Error** : You do not have permission to do that")

          #Check if ticket and open
          tchannel = await ticket_db.find_by_custom({"channelid":ctx_channel.id})
          if tchannel and tchannel["tstatus"] == 1: 
               towner = None
               try:
                    #Get owner and remove them from channel
                    towner = guild.get_member(tchannel["member_id"])
                    await ctx_channel.set_permissions(towner, view_channel=False,send_messages=False,read_message_history=False) 
               except (discord.HTTPException, discord.Forbidden,ValueError):
                    towner = None
               

          else:
               if interaction_or_channel == "i":
                    return await interaction.response.send_message(content="> **Error** : This is not a ticket or is no longer open",ephemeral=True)
               
               elif interaction_or_channel == "c":
                    return await ctx_channel.send("> **Error** : This is not a ticket or is no longer open")               
          
          #TranscriptEmbed
          CloseEmbed=discord.Embed(description=f"Ticket Closed by {action_author.mention}",colour=0xE0FF00)
          await ctx_channel.send(embed=CloseEmbed)

          CloseEmbed2=discord.Embed(description=f"Attempting to send transcript to <@{tchannel['member_id']}>",colour=0xE0FF00)
          close = await ctx_channel.send(embed=CloseEmbed2)

          CloseEmbed3=discord.Embed(description=f"```Support team ticket controls```",colour=0x2f3136)
          await ctx_channel.send(embed=CloseEmbed3,view = TButtons.ReOpenButtons(self.bot))

          #GetTranscript File/Link
          link = await TicketActions.generate_transcript_link(self,ctx_channel,guild)
          closeembed = await TicketActions.transcript_embed(self,ctx_channel,link,tchannel,action_author,tchannel["category"])

          tchannel["tstatus"] = 2
          tchan_id = tchannel["_id"]
          await ticket_db.update(tchannel)


          if towner:
               try:
                    await towner.send(embed=closeembed)
               except (discord.HTTPException, discord.Forbidden):
                    return await close.edit(embed=discord.Embed(description=f"Transcript failed sending to <@{tchannel['member_id']}> `Cannot send messages to this user`",colour=0xF44336))
               else:
                    return await close.edit(embed=discord.Embed(description=f"Transcript sent to <@{tchannel['member_id']}>",colour=0x00FF27))
          
          return await close.edit(embed=discord.Embed(description=f"Transcript failed sending to <@{tchannel['member_id']}> `User is null`",colour=0xF44336))



     async def delete_ticket(
          self,
          guild: discord.Guild,
          action_author: discord.Member,
          ctx_channel: discord.TextChannel,
          interaction_or_channel: str,
          interaction: discord.Interaction = None
          ):
          """
          Quickly delete a ticket from a command / interaction allowing for the ability to store a transcript
          """
          #CheckItsStaff
          StaffList = await utilmisc.build_stafflist(self)
          if action_author.id not in StaffList:
               if interaction_or_channel == "i":
                    return await interaction.response.send_message(content="> **Error** : You do not have permission to do that",ephemeral=True)
               
               elif interaction_or_channel == "c":
                    return await ctx_channel.send("> **Error** : You do not have permission to do that")

          #Check if ticket
          tchannel = await ticket_db.find_by_custom({"channelid":ctx_channel.id})
          if not tchannel:
               if interaction_or_channel == "i":
                    return await interaction.response.send_message(content="> **Error** : This is not a ticket",ephemeral=True)
               
               elif interaction_or_channel == "c":
                    return await ctx_channel.send("> **Error** : This is not a ticket")    

          category = tchannel["category"]
          towner_id = tchannel["member_id"]
          logchannel = await TicketActions.pick_channel(self,guild,category)

          chanclose = await ctx_channel.send(embed=discord.Embed(description=f"Sending transcript to {logchannel.mention}",colour=0xE0FF00))
          await ctx_channel.send(embed=discord.Embed(description=f"Ticked will be deleted in a few seconds",colour=0xFF2E00))
          
          #Transcript
          link = await TicketActions.generate_transcript_link(self,ctx_channel,guild)
          closeembed = await TicketActions.transcript_embed(self,ctx_channel,link,tchannel,action_author,category)
          await logchannel.send(f"||<@{towner_id}>||",embed=closeembed)

          #Physically delete it 
          await chanclose.edit(embed=discord.Embed(description=f"Transcript saved to {logchannel.mention}",colour=0x00FF27))
          await asyncio.sleep(1)
          await ctx_channel.delete()

          #Update DB
          tchannel["tstatus"] = 3
          await ticket_db.update(tchannel) 
     

     async def get_ticket_category_channel(
     self,
     ticket_type: str
     ) -> discord.TextChannel:
          """
          Get the ticket category quickly from the ticket type
          """
          category = 0
          if ticket_type not in self.bot.questions_data["Categories"]:
               return None
          
          ticket_type_info = self.bot.questions_data["Categories"][ticket_type]
          category = self.bot.get_channel(ticket_type_info["TicketCategory"])
          return category
          
     async def rename_ticket_channel(
          self,
          action_author: discord.Member,
          ctx_msg: discord.Message,
          ctx_channel: discord.TextChannel,
          new_name: str = None
     ) -> None:
          """
          Gives the ability to easily rename a ticket channel
          """
          tchannel = await ticket_db.find_by_custom({"channelid":ctx_channel.id})
          if not tchannel:
               return await ctx_channel.send("> **Error** : This is not a valid ticket")
          
          banned_words = ["1488"]
          if not new_name or any(word in new_name for word in banned_words):
               return await ctx_channel.send(f"> **Error** : {new_name} if not a valid ticket name ")


          StaffList = await utilmisc.build_stafflist(self)
          if action_author.id not in StaffList:
               return await ctx_channel.send("> **Error** : You do not have permission to do that")
    
          await ctx_channel.edit(name=new_name)
          await ctx_msg.delete()
          await ctx_channel.send(f"> Renamed channel to **{new_name}**",delete_after = 10)

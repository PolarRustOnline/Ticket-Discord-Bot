import discord
from discord.ext import commands
from TicketManagement.TicketActions import TicketActions
from db import ticket_db

#Close
class CloseButton(discord.ui.View):
  def __init__(self,bot):
     self.bot = bot
     super().__init__(timeout=None)

  @discord.ui.button(label="Close & Transcript",emoji="🔒", style=discord.ButtonStyle.red,custom_id="CloseButton")
  async def CloseButton(self, interaction: discord.Interaction, button: discord.ui.Button):
     await TicketActions.close_ticket(self,interaction.guild,interaction.user,interaction.channel,"i",interaction)


#Close & Delete
class CloseAndDelete(discord.ui.View):
  def __init__(self,bot):
     self.bot = bot
     super().__init__(timeout=None)

  @discord.ui.button(label="Close",emoji="🔒", style=discord.ButtonStyle.grey,custom_id="CloseAndDeleteClose")
  async def CloseAndDeleteClose(self, interaction: discord.Interaction, button: discord.ui.Button):
     await TicketActions.close_ticket(self,interaction.guild,interaction.user,interaction.channel,"i")

  @discord.ui.button(label="Delete",emoji="⛔", style=discord.ButtonStyle.grey,custom_id="CloseAndDeleteDelete")
  async def CloseAndDeleteDelete(self, interaction: discord.Interaction, button: discord.ui.Button):
     await TicketActions.delete_ticket(self,interaction.guild,interaction.user,interaction.channel,"i")    


class ReOpenButtons(discord.ui.View):
  def __init__(self,bot):
     self.bot = bot
     super().__init__(timeout=None)

  @discord.ui.button(label="Reopen",emoji="🔓", style=discord.ButtonStyle.grey,custom_id="Reopen")
  async def Reopen(self, interaction: discord.Interaction, button: discord.ui.Button):
     tchannel = await ticket_db.find_by_custom({"channelid":interaction.channel_id})
     if tchannel and tchannel["tstatus"] == 2:

          await interaction.response.send_message(content="\u200b",ephemeral=True)
          towner = interaction.guild.get_member(tchannel["member_id"])
          if towner:
               await interaction.channel.set_permissions(towner, view_channel=True,send_messages=True,read_message_history=True,embed_links=True,attach_files=True)
          else:
               return await interaction.response.send_message(content="**Error** : User is no longer in the discord...",ephemeral=True)

          tchannel["tstatus"] = 1
          await ticket_db.update(tchannel)

          CloseEmbed=discord.Embed(description=f"Ticket Reopened by {interaction.user.mention}",colour=0xE0FF00)
          await interaction.channel.send(
               embed=CloseEmbed,
               view = CloseAndDelete(self.bot)
               )
          
          category = await TicketActions.get_ticket_category_channel(self,tchannel["category"])
          if category != interaction.channel.category:
               await interaction.channel.edit(category=category)

     else:
        return await interaction.response.send_message(content="**Error** : Ticket is already open?",ephemeral=True)

  @discord.ui.button(label="Delete",emoji="⛔", style=discord.ButtonStyle.grey,custom_id="DeleteCloseButton")
  async def DeleteCloseButton(self, interaction: discord.Interaction, button: discord.ui.Button):
     await TicketActions.delete_ticket(self,interaction.guild,interaction.user,interaction.channel,"i")       

class Buttons(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.bot.add_view(CloseButton(self.bot))
    self.bot.add_view(CloseAndDelete(self.bot))
    self.bot.add_view(ReOpenButtons(self.bot))

  @commands.Cog.listener()
  async def on_ready(self):
    print(f"{self.__class__.__name__} Cog has been loaded\n-----")


async def setup(bot):
  await bot.add_cog(Buttons(bot))





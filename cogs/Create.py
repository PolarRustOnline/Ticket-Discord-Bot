import string
import random
import discord
import datetime
from discord import ui
from datetime import datetime
from discord.ext import commands, tasks
from cogs.TButtons import *
from db import ticket_db

class DropdownTicketOptions(discord.ui.Select):
     def __init__(self,bot):
          self.bot = bot
          options = []
          for category in self.bot.questions_data["Categories"]:
               options.append(discord.SelectOption(label=category, value=category,description=self.bot.questions_data["Categories"][category]["Description"],emoji=self.bot.questions_data["Categories"][category]["Emoji"]))
          super().__init__(options = options, placeholder="Select a reason to open a ticket",min_values = 1,max_values = 1,custom_id="TicketSelectList")

     async def callback(self, interaction: discord.Interaction):
          if not self.values:
               return await interaction.response.send_message(content=f"> Something went wrong...",ephemeral=True)
          await Creation.build_ticket(self,interaction,interaction.guild,interaction.user,self.values[0])

class DropdownTicketOptionsView(discord.ui.View):
  def __init__(self,bot):
    self.bot = bot
    super().__init__(timeout=None)
    self.add_item(DropdownTicketOptions(self.bot))

#CreateAModelWithThePassedQuestions
class ModelWithQuestions(ui.Modal):
     def __init__(self,bot,title,questions):
          self.bot = bot
          super().__init__(timeout=None,title=title)
          for q in questions:
               if q["type"] == "short":
                    q = ui.TextInput(label=q["q"],placeholder=q["p"],style=discord.TextStyle.short,max_length=q["max_length"],min_length=q["min_length"],required=q["required"])  
               else:
                    q = ui.TextInput(label=q["q"],placeholder=q["p"],style=discord.TextStyle.long,max_length=q["max_length"],min_length=q["min_length"],required=q["required"])  
               ui.Modal.add_item(self,q)
          

     #Submit -> Make a ticket!
     async def on_submit(self, interaction: discord.Interaction):
          answered_questions = {}
          for response in self.children:
               answered_questions[response.label] = response.value
          await Creation.generate_make_ticket(self.bot,interaction,interaction.guild,interaction.user,self.title,answered_questions)


class Creation(commands.Cog):
     def __init__(self, bot):
          self.bot = bot
          self.bot.add_view(DropdownTicketOptionsView(self.bot))

     @commands.Cog.listener()
     async def on_ready(self):
          print(f"{self.__class__.__name__} Cog has been loaded\n-----")

     @commands.command()
     async def setembed(self, ctx):
          await ctx.message.delete()
          txt = (f"Welcome to the **{self.bot.data['Server_Name']}** Support & Ticket System.\n\n"
          f"Open a ticket that fits the category of the issue you need assistance with!\n\n"
          f"Abuse of this feature will result in the removal your ability to use it,\n"
          f"⬇️ **To open a ticket, select the relavent option from the dropdown underneath**")
          await ctx.send(content = str(txt),view = DropdownTicketOptionsView(self.bot))
          
     async def build_ticket(self,
     interaction: discord.Interaction,
     guild: discord.Guild,
     member: discord.Member,
     ticket_type: str
     ) -> None:
     

          #Already has this type of ticket
          ticket = await ticket_db.find_by_custom({"member_id":member.id,"tstatus":1,"category":ticket_type})
          if ticket:
               return await interaction.response.send_message(content=f"You already have a ticket open under **{ticket_type}**",ephemeral=True)
          
          #Trying to open a category that doesn't exit
          if ticket_type not in self.bot.questions_data["Categories"]:
               return await interaction.response.send_message(content=f"> **Error** : {ticket_type} is not a valid ticket type 0.o?",ephemeral=True)
          
          #Check for questions 
          ticket_type_info = self.bot.questions_data["Categories"][ticket_type]
          if ticket_type_info["Questions"]:
               try:
                    return await interaction.response.send_modal(ModelWithQuestions(self.bot,ticket_type,ticket_type_info["Questions"]))
               except discord.errors.NotFound:
                    return
          else:
               return await Creation.generate_make_ticket(self,interaction,guild,member,ticket_type)


     async def generate_make_ticket(
          bot = None, 
          interaction: discord.Interaction = None,
          guild: discord.Guild = None,
          member: discord.Member = None,
          ticket_type: str = "",
          questions: dict = None
          ) -> None:

          

          #FindCategoryFromConfig
          ticket_type_info = bot.questions_data["Categories"][ticket_type]
          category = bot.get_channel(ticket_type_info["TicketCategory"])


          #DMUserUponCreation
          ticket_id_referance = f"{ticket_type_info['ChannelShortname']}-".replace(" ","") + (''.join(random.choices((string.ascii_letters + string.digits), k=6)))
          

          question_text = ""
          if questions:
               for que in questions:
                    question = que
                    answer = questions[que]
                    question_text += f"\n**{question}**\n```{answer}```"
          embed = discord.Embed(
               description=question_text,
               colour=0x3B87FB,
               timestamp=datetime.now()
          )
          embed.set_footer(text = f"Send from the {bot.data['Server_shortname']} Staff Team - Keep your dms open")
          embed.set_image(url=bot.data["Big_thumbnail_url"])

          #SetChannelPermissions
          overwrites = {
               guild.default_role: discord.PermissionOverwrite(view_channel=False,send_messages=False, read_message_history=False),
               member: discord.PermissionOverwrite(view_channel=True,send_messages=True,read_message_history=True,embed_links=True,attach_files=True)
          } 
          for role_id in ticket_type_info["RolesInChannel"]:
               overwrites[guild.get_role(role_id)] = discord.PermissionOverwrite(view_channel=True,send_messages=True,read_message_history=True,embed_links=True,attach_files=True)

          #Format the ticket text
          ticket_text = f"{member.mention} has made a **{ticket_type}** Ticket: \n" + question_text + "\n\nTo close this ticket click the 🔒 • Close Button"
          if "TicketPingRole" in ticket_type_info and ticket_type_info["TicketPingRole"]:
               ticket_text = f"<@&{ticket_type_info['TicketPingRole']}> " + ticket_text

          
          
          #PhsyicallyMakeTheChannel
          try:
               channel = await guild.create_text_channel(
                    name=f"{ticket_id_referance}",
                    overwrites=overwrites,
                    category=category
               )
          except (discord.HTTPException, discord.Forbidden):
               return await interaction.response.send_message(content=f"**Error** : We currently have too many of those tickets - please try again shortly",ephemeral=True)
         
          await interaction.response.send_message(content=f"Ticket has been created -> <#{channel.id}>",ephemeral=True)

          ticket_msg = await channel.send(content=ticket_text,view=CloseButton(bot))

          

          await ticket_db.insert({
               "_id":ticket_id_referance,
               "member_id":member.id,
               "member_name":member.name,
               "category":ticket_type,
               "tstatus":1,
               "tmsg_id": ticket_msg.id,
               "channelid":channel.id,
               "spoken_users":{},
               "creationtime":datetime.now(),
               "claimed":None,
          })



  
async def setup(bot):
  await bot.add_cog(Creation(bot))
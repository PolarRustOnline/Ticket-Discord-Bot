import discord

class utilmisc():
    def __init__(self, bot):
        self.bot = bot
  
    async def build_stafflist(self):
        StaffList = []
        guild = self.bot.get_guild(self.bot.data["StaffListInfo"]["Guild_ID"])
        for r in self.bot.data["StaffListInfo"]["Roles"]:
            try:
                role = guild.get_role(r)
            except (discord.HTTPException, discord.Forbidden):
                role = None
        
            if role:
                StaffList.extend([member.id for member in role.members if member.id not in StaffList])

        return StaffList
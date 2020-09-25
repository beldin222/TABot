import discord
from discord.ext import commands

class Queue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.get_cog("Config") 
        self.queue = {}
        self.voice_channel_cache = {}

    def next(self, guild_id):
        return self.queue[guild_id].pop(0)

    # Get users already waiting in waiting rooms. Used when bot first starts up.
    @commands.Cog.listener()
    async def on_ready(self):
        for guild_id in self.config.parser.sections()[1:]:
            guild_id = int(guild_id)
            channel_id = int(self.config.get_server_config(guild_id, "waiting_voice_id"))
            channel = self.bot.get_channel(channel_id)
            if channel == None and channel_id != None:
                # TODO: Use a proper logger                
                print("Invalid waiting channel! ID:", channel_id)
                continue
            self.queue.update({guild_id: channel.members})

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_channel_id = self.config.get_server_config(member.guild.id, "waiting_voice_id")
        # TODO: Compare IDs directly since it's faster (if it won't break)
        if before.channel is None and after.channel == self.get_voice_cached(voice_channel_id):
            await self.on_join(member)
        elif before.channel is self.get_voice_cached(voice_channel_id) and after.channel == None:
            await self.on_leave(member)
            
    async def on_join(self, member):
        guild_id = member.guild.id
        if not guild_id in self.queue:
            self.queue[guild_id] = []
        # Doing this has multiple advantages, including not searching for the user again
        # and being consistent with the get_waiting_users function, since channel.members returns a list of `discord.Member`s
        self.queue[guild_id].append(member)
    
    async def on_leave(self, member):
        self.queue[member.guild.id].remove(member)
    
    # TODO: Maybe figure out another cleaner way to cache channels?
    def get_voice_cached(self, channel_id):
        channel_id = int(channel_id)
        if channel_id in self.voice_channel_cache:
            return self.voice_channel_cache[channel_id]
        else:
            channel = self.voice_channel_cache[channel_id] = self.bot.get_channel(channel_id)
            return channel

def setup(bot):
    bot.add_cog(Queue(bot))
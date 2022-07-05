import os
import logging

import discord
from discord.ext import commands

import utils
import AMP as AMP
import DB as DB


def db_bot_settings():
    #!TODO!
    print('Get all the DB config settings')



class DB_Module(commands.Cog):
    def __init__ (self,client:commands.Bot):
        self._client = client
        self.name = os.path.basename(__file__)

        self.logger = logging.getLogger(__name__) #Point all print/logging statments here!
        self.logger.info(f'**SUCESS** Loading **{self.name.replace("db","DB")}**')

        self.AMPHandler = AMP.getAMPHandler()
        self.AMP = self.AMPHandler.AMP#Main AMP object
        self.AMPInstances = self.AMPHandler.AMP_Instances #Main AMP Instance Dictionary

        self.DBHandler = DB.getDBHandler()
        self.DB = self.DBHandler.DB #Main Database object
        self.DBConfig = self.DBHandler.DBConfig

        self.uBot = utils.botUtils(client)
        self.dBot = utils.discordBot(client)

        self.uBot.sub_command_handler('bot',self.db_bot_channel)
     

    @commands.Cog.listener('on_message')
    async def on_message(self,message:discord.Message):
        if message.content.startswith(self._client.command_prefix):
            return message
        if message.author != self._client.user:
            self.logger.info(f'On Message Event for {self.name}')
            return message

    @commands.Cog.listener('on_member_update')
    async def on_member_update(self,user_before:discord.User,user_after:discord.User):
        #Lets see if the name is different from before.
        if user_before.name != user_after.name:
            #Lets look up the previous ID to gaurentee a proper search, could use the newer user ID; both in theory should be the same.
            db_user = self.DB.GetUser(user_before.id)
            #If we found the DB User
            if db_user != None:
                db_user.DiscordName = user_after.name
            else: #Lets Add them with the info we have!
                self.DB.AddUser(DiscordID= user_before.id, DiscordName= user_after.name)

            self.logger.info(f'User Update {self.name}: {user_before.name} into {user_after.name}')
            return user_after

    #This is called when a message in any channel of the guild is edited. Returns <message> object.
    @commands.Cog.listener('on_message_edit')
    async def on_message_edit(self,message_before:discord.Message,message_after:discord.Message):
        """Called when a Message receives an update event. If the message is not found in the internal message cache, then these events will not be called. Messages might not be in cache if the message is too old or the client is participating in high traffic guilds."""
        if message_before.author != self._client.user:
            self.logger.info(f'Edited Message Event for {self.name}')
            return message_before,message_after

    @commands.Cog.listener('on_reaction_add')
    async def on_reaction_add(self,reaction:discord.Reaction,user:discord.User):
        """Called when a message has a reaction added to it. Similar to on_message_edit(), if the message is not found in the internal message cache, then this event will not be called. Consider using on_raw_reaction_add() instead."""
        print(f'{user.name} Added the Reaction: {reaction}')
        return reaction,user

    @commands.Cog.listener('on_reaction_remove')
    async def on_reaction_remove(self,reaction:discord.Reaction,user:discord.User):
        """Called when a message has a reaction removed from it. Similar to on_message_edit, if the message is not found in the internal message cache, then this event will not be called."""
        print(f'{user.name} Removed the Reaction: {reaction}')
        return reaction,user

    
    @commands.Cog.listener('on_member_remove')
    async def on_member_remove(self,member:discord.Member):
        print(f'Member has left the server {member.name}')
        return member
        
    @utils.role_check()
    @commands.hybrid_group()
    async def user(self,context:commands.Context):
        if context.invoked_subcommand is None:
            await context.send('Please try your command again...')

    @user.command(name='info')
    @utils.role_check()
    async def user_info(self,context:commands.Context,user:str=None):
        """DB User Information"""
        #Call on DB User specific Info from here
        self.logger.info('User Information')

    @user.command(name='test')
    @utils.role_check()
    async def user_test(self,context:commands.Context,user:str=None):
        """DB User Test Function"""
        #print(dir(context))
        cur_user = self.uBot.userparse(context = context,guild_id=context.guild.id,parameter = user)
        self.logger.info('User Test Function')
        await context.send(cur_user)

    # @commands.hybrid_command(name='dbwhitelist')
    # @utils.role_check()
    # async def server_whitelist_true(self,context,server,var='false'):
    #     """Set DB Server Whitelist"""
    #     server = await self.uBot.serverparse(context,context.guild.id,server)
    #     if var.lower() == 'true':
    #         self.DB.getServer(server.FriendlyName).Whitelist = True
    #     if var.lower() == 'false':
    #         self.DB.getServer(server.FriendlyName).Whitelist = False
    #     await context.send(f"Server: {server.FriendlyName}, Whitelist set to : {var}")

    @commands.hybrid_group(name='channel')
    @utils.role_check()
    async def db_bot_channel(self,context:commands.Context):
        if context.invoked_subcommand is None:
            await context.send('Invalid command passed...')
        
    @db_bot_channel.command(name='whitelist')
    @utils.role_check()
    async def db_bot_channel_whitelist(self,context:commands.Context,id:str):
        self.logger.info('Bot Channel Whitelist...')

        channel = self.uBot.channelparse(id,context,context.guild.id)
        if channel == None:
            return await context.reply(f'Unable to find the Discord Channel: {id}')
        else:
            self.DBConfig.SetSetting('WhitelistChannel',channel.id)
            await context.send(f'Set Bot Channel Whitelist to {channel.name}')

    #!TODO! This function doesn't exist yet.
    async def db_bot_settings(self):
        """This is accessed through bot settings in Gatekeeper.py"""
        settings = self.DBConfig.GetSettingList()
        print(settings)
        return settings

    @commands.hybrid_group(name='dbserver')
    @utils.role_check()
    async def db_server(self,context:commands.Context):
        if context.invoked_subcommand is None:
            await context.send('Invalid command passed...')

    @db_server.command(name='cleanup')
    @utils.role_check()
    async def db_server_cleanup(self,context:commands.Context):
        """This is used to remove un-used DBServer entries and update names of existing servers."""
        self.logger.info('Database Clean-Up in progress...')

        db_server_list = self.DB.GetAllServers() 

        for server in db_server_list:
            if server.InstanceID not in self.AMPInstances:
                db_server = self.DB.GetServer(InstanceID = server.InstanceID)
                db_server.delServer()
            if server.InstanceID in self.AMPInstances:
                for instance in self.AMPInstances:
                    if self.AMPInstances[instance].InstanceID == server.InstanceID:
                            server.FriendlyName = self.AMPInstances[instance].FriendlyName

    #!TODO! This Function needs to be laid out and tested.
    @db_server.command(name='swap')
    @utils.role_check()
    async def db_server_instance_swap(self,context,old_server,new_server):
        """This will be used to swap Instance ID's with an existing AMP Instance"""
        self.logger.info()
        old_server = self.uBot.serverparse(context,context.guild.id)

async def setup(client):
    await client.add_cog(DB_Module(client))
# Imports START
import discord
# import nextcord
import asyncio
import datetime
import requests
import openai
import os
# import socket

from dotenv import load_dotenv
from opengsq.protocols import Source
from discord.ext import commands
import aiohttp
import asyncio

import logging

logging.basicConfig(level=logging.INFO, filename='bot_log.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')


# Imports END
gpt_headers =  {
    'content-type': 'application/json',
    'Content-Type': 'application/json',
    'X-RapidAPI-Key': '491ce3edf8msh10db694d3787c7fp146ebajsn6a823d2c4b3f',
    'X-RapidAPI-Host': 'chat-gpt26.p.rapidapi.com'
  }
webhook_url = "https://discord.com/api/webhooks/1220067617868484729/1yxYhBAwvKqb5aJtlRbVh-usbwwRqoF93vzc4GmL19VWTbc3-cJwOpsaQ0Z2JbI1DIfS"

conversations = {}
# Init variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GUILD_ID = os.getenv('GUILD_ID')
JOIN_CHANNEL_ID = os.getenv('JOIN_CHANNEL_ID')

# Client start
bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())

async def load_extensions():
    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
            await bot.load_extension(f"cogs.{f[:-3]}")
                    
    

# Bot EVENTS
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to the {GUILD}')

@bot.event
async def on_member_join(member):
    logging.info(f"Member joined: {member}")
    channel = bot.get_channel(int(JOIN_CHANNEL_ID))
    logging.info(f"Channel: {channel}")

    print("Channel: ", channel)
    if channel:
        embed = discord.Embed(title="Здарова Сталкер!", description=f"{member.mention} вошел в Зону Отчуждения", color=0x00ff00)
        embed.add_field(name="Аккаунт создан", value=member.created_at.strftime("%A, %B %d, %Y at %H:%M %p"), inline=True)
        if getattr(member, 'avatar_url', None) is not None:
            embed.set_thumbnail(url=member.avatar_url)
        await channel.send(member.mention)
        await channel.send(embed=embed)

@bot.event
async def on_message(message):
    # Не отвечаем на сообщения от самого бота
    if message.content.startswith('!ау'):
        channel_id = message.channel.id
            
            # Retrieve the current conversation history for the channel
        if channel_id in conversations:
            chat_history = conversations[channel_id]
        else:
            chat_history = []
            conversations[channel_id] = chat_history
        
        user_query = message.content[len('!ау '):]
        
        # Persistent character context and introduction for new conversation
        if not chat_history:  # if conversation history is empty
            context = "The year is 2008. I am Doom, a stalker in the Chernobyl Exclusion Zone. Your answer needs to be no more than 317 characters."
            chat_history.append({"role": "system", "content": context})

        chat_history.append({"role": "user", "content": user_query})

            # Construct the prompt with all preceding messages
        async with message.channel.typing():
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=chat_history,
                max_tokens=150
            )

            # Get the response and add it to history
            bot_response = response['choices'][0]['message']['content']
            chat_history.append({"role": "assistant", "content": bot_response})

    # Send the response to the Discord channel
            await asyncio.sleep(3)
            await message.channel.send(bot_response)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('У вас нет необходимой роли для выполнения этой команды')


async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())



     


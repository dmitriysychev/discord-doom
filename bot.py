# Imports START
import discord
# import nextcord
import asyncio
import datetime
import requests

import os
# import socket

from dotenv import load_dotenv
from opengsq.protocols import Source
from discord.ext import commands
import aiohttp
import asyncio
# Imports END
gpt_headers =  {
    'content-type': 'application/json',
    'Content-Type': 'application/json',
    'X-RapidAPI-Key': '491ce3edf8msh10db694d3787c7fp146ebajsn6a823d2c4b3f',
    'X-RapidAPI-Host': 'chat-gpt26.p.rapidapi.com'
  }
webhook_url = "https://discord.com/api/webhooks/1220067617868484729/1yxYhBAwvKqb5aJtlRbVh-usbwwRqoF93vzc4GmL19VWTbc3-cJwOpsaQ0Z2JbI1DIfS"


# Init variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GUILD_ID = os.getenv('GUILD_ID')

# Client start
bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())

async def load_extension():
    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
            await bot.load_extension("cogs." + f[:-3])
                        
    

# Bot EVENTS
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to the {GUILD}')
    
@commands.command(name="ау")
async def talk(ctx, *args):
    body = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": " ".join(args)
            }
        ]
    }

    response = requests.post("https://chat-gpt26.p.rapidapi.com/", headers=gpt_headers, json=body)
    data = response.json()['choices'][0]['message']['content']

    await ctx.send(data)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('У вас нет необходимой роли для выполнения этой команды')

@bot.event
async def on_member_join(member):
    # await bot.send_message(member, 'Prompt.')
    # m = await bot.wait_for_message(author=member, channel=member)
    # if m.content == 'key':
    #     # give the user the role
    #     await bot.send_message(member, 'Role added')
    # else:
    #     await bot.send_message(member, 'Incorrect key')
    pass
bot.add_command(talk)

async def main():
    async with bot:
        await load_extension()
        await bot.start(TOKEN)
# bot.run(TOKEN)


     


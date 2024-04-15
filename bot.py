# Imports START
import discord
# import nextcord
import asyncio
import datetime
import requests
import openai
import os
import sqlite3
import subprocess
import aiohttp
import asyncio
import logging


from dotenv import load_dotenv
from opengsq.protocols import Source


logging.basicConfig(level=logging.INFO, filename='bot_log.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')



webhook_url = "https://discord.com/api/webhooks/1220067617868484729/1yxYhBAwvKqb5aJtlRbVh-usbwwRqoF93vzc4GmL19VWTbc3-cJwOpsaQ0Z2JbI1DIfS"

conversations = {}
achievements = {
    "Опытный мужик": {"message_count": 500, "description": "Отправил 500 сообщений!"},
    "Сталкер со стажем": {"voice_minutes": 200, "description": "Потратил 200 минут в войс чате!"}
}

#
# Init variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GUILD_ID = os.getenv('GUILD_ID')
JOIN_CHANNEL_ID = os.getenv('JOIN_CHANNEL_ID')

# Client start
bot = discord.Bot(intents=discord.Intents.all())
conn = sqlite3.connect('achievements.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS user_activity (user_id INTEGER PRIMARY KEY, message_count INTEGER, voice_minutes INTEGER, achievements TEXT)''')
conn.commit()

def load_extensions():
    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
            bot.load_extension(f"cogs.{f[:-3]}")
                  

async def check_achievements(user_id):
    c.execute('SELECT message_count, voice_minutes, achievements FROM user_activity WHERE user_id = ?', (user_id,))
    data = c.fetchone()
    current_achievements = data[2].split(',') if data[2] else []
    
    for key, value in achievements.items():
        if key not in current_achievements:
            if (value.get('message_count', float('inf')) <= data[0] or
                value.get('voice_minutes', float('inf')) <= data[1]):
                current_achievements.append(key)
                await bot.get_user(user_id).send(f"Поздравляю! Ты получил достижение '{key}' за то что {value['description']}")

    # Update achievements in the database
    c.execute('UPDATE user_activity SET achievements = ? WHERE user_id = ?', (','.join(current_achievements), user_id))
    conn.commit()

# Bot EVENTS
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to the {GUILD}')

@bot.event
async def on_member_join(member):
    logging.info(f"Member joined: {member}")
    channel = bot.get_channel(int(JOIN_CHANNEL_ID))
    if channel:
        embed = discord.Embed(title="Здарова Сталкер!", description=f"{member.mention} вошел в Зону Отчуждения", color=0x00ff00)
        embed.add_field(name="Аккаунт создан", value=member.created_at.strftime("%A, %B %d, %Y at %H:%M %p"), inline=True)
        if getattr(member, 'avatar_url', None) is not None:
            embed.set_thumbnail(url=member.avatar_url)
        await channel.send(member.mention)
        await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Update message count in the database
    c.execute('SELECT message_count FROM user_activity WHERE user_id = ?', (message.author.id,))
    data = c.fetchone()
    if data:
        logging.info(f"Data found for user{message.author} -  {data}")
        c.execute('UPDATE user_activity SET message_count = message_count + 1 WHERE user_id = ?', (message.author.id,))
    else:
        logging.info(f"Data not found found for user{message.author} - incrementing message count")
        c.execute('INSERT INTO user_activity (user_id, message_count, voice_minutes, achievements) VALUES (?, 1, 0, "")', (message.author.id,))
    conn.commit()
    await check_achievements(message.author.id)
    #Не отвечаем на сообщения от самого бота
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


load_extensions()

bot.run(TOKEN)




     


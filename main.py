# Imports START
import discord
# import nextcord
import asyncio
import datetime

import os
import socket

from dotenv import load_dotenv
from opengsq.protocols import Source
from discord.ext import commands
# Imports END

webhook_url = "https://discord.com/api/webhooks/1220067617868484729/1yxYhBAwvKqb5aJtlRbVh-usbwwRqoF93vzc4GmL19VWTbc3-cJwOpsaQ0Z2JbI1DIfS"


# Init variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
gp_list = ['Экологи','Долг','Воля','Нейтралы','Бандиты','Грех','Ворон','Ренегаты','Чистое Небо','Черный рынок','Наёмники']
admin_roles = ['Создатель','Тех. Администратор','Администратор']

low_roles = ['Ст. РП Куратор','Ст. Ивентолог','РП Куратор','Ивентолог']
all_admin_roles = ['Создатель','Тех. Администратор','Администратор']
# Dictionary to store tasks associated with users
scheduled_tasks = {}

# Client start
bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())


# Bot EVENTS
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to the {GUILD}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('У вас нет необходимой роли для выполнения этой комманды')

# Bot COMMANDS
@bot.slash_command(name='test_command', guild_ids=[1009672589825814529])
async def test(ctx):
    await ctx.respond('TEST')



@bot.slash_command(name='adm', description='Команда которая выводит состав курации и ивентологов',guild_ids=[1009672589825814529])
@commands.has_any_role('Создатель','Тех. Администратор','Администратор')
async def adm(ctx):
    embed = discord.Embed(title="Курация и Ивентологи", color=discord.Color.green())

    for role_name in low_roles:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            members_with_role = [member.mention for member in ctx.guild.members if role in member.roles]
            if members_with_role:
                embed.add_field(name=f"**{role_name}**", value="\n".join(members_with_role), inline=False)
            else:
                embed.add_field(name=f"**{role_name}**", value="Отсутствует", inline=False)
    await ctx.respond(embed=embed)

@bot.slash_command(name='cls', description='Команда которая чистит количество сообщений',guild_ids=[1009672589825814529])
@commands.has_any_role('Создатель','Тех. Администратор','Администратор')
async def cls(ctx, amount: int):
        # Check if the user has permissions to manage messages

    # Delete 'amount' of messages + 1 for the command message
    await ctx.channel.purge(limit=amount + 1)
    await ctx.response.send_message(f'{amount} сообщений очищено {ctx.author.mention}')


@bot.slash_command(name='gp', description='Команда которая выводит кураторов и их группировки',guild_ids=[1009672589825814529])
@commands.has_any_role('Создатель','Тех. Администратор','Администратор')
async def gp(ctx):
    kurator_roles = ['Ст. РП Куратор','РП Куратор']

    # Get role objects for kurator_roles
    kurator_role_objects = [discord.utils.get(ctx.guild.roles, name=role_name) for role_name in kurator_roles]
    # Filter out None values (roles that couldn't be found)
    kurator_role_objects = [role for role in kurator_role_objects if role is not None]
    
    if not kurator_role_objects:
        await ctx.send("Could not find any of the specified kurator roles.")
        return
    
    # Collect members with their roles
    member_roles = {member: set(member.roles) for member in ctx.guild.members}
    embed = discord.Embed(title="Списки группировок и кураторы", color=0x00ff00)

    for role_name in gp_list:
        matching_roles = [role for role in ctx.guild.roles if role_name.lower() in role.name.lower()]
        if matching_roles:
            for role in matching_roles:
                if role.name in ["🩸 • Враг Монолита", "Отдаёт долг родине 🥺"]:
                    continue  # Skip these roles
                member_found = False
                member_count = sum(1 for member, roles in member_roles.items() if role in roles and not any(kurator_role in roles for kurator_role in kurator_role_objects))
               
                for member, roles in member_roles.items():
                    if (role in roles) and any(kurator_role in roles for kurator_role in kurator_role_objects):
                        role_embed = f"{role.name} ({member_count} игроков)"
                        embed.add_field(name=role_embed, value=member.mention, inline=False)
                        member_found = True
                        break
                if not member_found:
                    role_embed = f"{role.name} ({member_count} игроков)"
                    embed.add_field(name=role_embed, value="Не найдено кураторов", inline=False)
    await ctx.respond(embed=embed)

@bot.slash_command(name='ro', description='Команда которая выдает РО',guild_ids=[1009672589825814529])
@commands.has_any_role('Создатель','Тех. Администратор','Администратор')
async def ro(ctx, member: discord.Member, duration: int, reason: str):
    role = discord.utils.get(ctx.guild.roles, name='❌ • Read Only')
    embed = discord.Embed(title='Наказание!', color=discord.Color.red())
   
    # Give the user the specified role
    await member.add_roles(role)
    
    # Calculate the time when the role should be removed
    removal_time = datetime.datetime.utcnow() + datetime.timedelta(days=duration)

    # Schedule a task to remove the role after 'duration' days
    task = bot.loop.create_task(remove_role_after(member, role, removal_time))
    scheduled_tasks[member.id] = task
    embed.add_field(name="Кем выдано",value=ctx.author.mention)
    embed.add_field(name="Наказание", value=f"{member.mention} вам была выдана роль: {role.mention} на {duration} d.", inline=False)
    embed.add_field(name='Причина', value = reason)
    await ctx.respond(member.mention,embed = embed)

async def remove_role_after(member, role, removal_time):
    while True:
        # Wait until the removal time
        await asyncio.sleep((removal_time - datetime.datetime.utcnow()).total_seconds())
        # Remove the role
        await member.remove_roles(role)

        # Remove the task from the dictionary
        del scheduled_tasks[member.id]


class OpenView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, category_id_tickets):
        super().__init__()
        self.category_id_tickets = category_id_tickets
        
    @discord.ui.button(label="Открыть тикет", style=discord.ButtonStyle.success, emoji="😎") # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        ctx = interaction.channel
        category_id = self.category_id_tickets
        category = ctx.guild.get_channel(category_id)

        if category:
            ticket_channel = await category.create_text_channel(name=f'ticket-{interaction.user.name}')

            await ticket_channel.set_permissions(ctx.guild.default_role, view_channel=False)
            await ticket_channel.set_permissions(interaction.user, view_channel=True, read_messages=True, send_messages=True)
            embed = discord.Embed(title='Что у вас случилось?', description='Кратко опишите проблему чтобы мы могли вам помочь.', color=discord.Color.green())
            await ticket_channel.send(interaction.user.mention)
            await ticket_channel.send(embed=embed, view=CloseView(ticket_channel))
            

            await interaction.response.send_message(f"Тикет создан! Найти его можно тут -> {ticket_channel.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message("Не могу найти категорию")

class CloseView(discord.ui.View):
    def __init__(self, ticket_channel):
        super().__init__()
        self.ticket_channel = ticket_channel

    @discord.ui.button(label="Закрыть тикет", style=discord.ButtonStyle.danger, emoji="😎") # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        # Check if the user has permission to close the ticket (only the ticket author should have permission)
        if interaction.channel.name.startswith('ticket-'):
        # Check if the author of the message is the ticket creator
            member_roles = [role.name for role in interaction.user.roles]
            allow =  any(role in all_admin_roles for role in member_roles)
            if interaction.channel.name[len('ticket-'):] == interaction.user or allow:
                await interaction.response.send_message("Тикет будет закрыт")
                await interaction.channel.delete()
            else:
                await interaction.response.send_message("Вы можете закрывать только свои тикеты")
        else:
            await interaction.response.send_message("Команда может быть использована только в тикете")

@bot.slash_command(name='show_test', description='TEST',guild_ids=[1009672589825814529])
async def show_test(ctx, title):
    embed = discord.Embed(title=title, description="Если вам требуется помощь нажмите на кнопку ниже", color=discord.Color.gold())
    

    # Sending the embed with the button
    await ctx.send(embed=embed, view=OpenView(1010800079789105182))



bot.run(TOKEN)



import common
import asyncio
import datetime

gp_list = ['Экологи','Долг','Воля','Нейтралы','Бандиты','Грех','Ворон','Ренегаты','Чистое Небо','Черный рынок','Наёмники']
admin_roles = ['Создатель','Тех. Администратор','Администратор']

low_roles = ['Ст. РП Куратор','Ст. Ивентолог','РП Куратор','Ивентолог']
all_admin_roles = ['Создатель','Тех. Администратор','Администратор']
active_polls = set()


class Administrative(common.commands.Cog):
    scheduled_task = {}

    def __init__(self, bot):
        self.bot = bot
   
    
    @common.commands.slash_command(name='adm', description='Команда которая выводит состав курации и ивентологов',guild_ids=[common.guild_id])
    @common.commands.has_any_role('Создатель','Тех. Администратор','Администратор')
    async def adm(self, ctx):
        embed = common.discord.Embed(title="Курация и Ивентологи", color=common.discord.Color.green())

        for role_name in low_roles:
            role = common.discord.utils.get(ctx.guild.roles, name=role_name)
            if role:
                members_with_role = [member.mention for member in ctx.guild.members if role in member.roles]
                if members_with_role:
                    embed.add_field(name=f"**{role_name}**", value="\n".join(members_with_role), inline=False)
                else:
                    embed.add_field(name=f"**{role_name}**", value="Отсутствует", inline=False)
        await ctx.respond(embed=embed)


    @common.commands.slash_command(name='gp', description='Команда которая выводит кураторов и их группировки',guild_ids=[common.guild_id])
    @common.commands.has_any_role('Создатель','Тех. Администратор','Администратор')
    async def gp(self, ctx):
        kurator_roles = ['Ст. РП Куратор','РП Куратор']

        # Get role objects for kurator_roles
        kurator_role_objects = [common.discord.utils.get(ctx.guild.roles, name=role_name) for role_name in kurator_roles]
        # Filter out None values (roles that couldn't be found)
        kurator_role_objects = [role for role in kurator_role_objects if role is not None]
        
        if not kurator_role_objects:
            await ctx.send("Could not find any of the specified kurator roles.")
            return
        
        # Collect members with their roles
        member_roles = {member: set(member.roles) for member in ctx.guild.members}
        embed = common.discord.Embed(title="Списки группировок и кураторы", color=0x00ff00)

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
        
    @common.commands.slash_command(name='cls', description='Команда которая чистит количество сообщений',guild_ids=[common.guild_id])
    @common.commands.has_any_role('Создатель','Тех. Администратор','Администратор')
    async def cls(self, ctx, amount: int):
            # Check if the user has permissions to manage messages
        # Delete 'amount' of messages + 1 for the command message
        await ctx.channel.purge(limit=amount + 1)
        await ctx.response.send_message(f'{amount} сообщений очищено', ephemeral=True)

    @common.commands.slash_command(name='ro', description='Команда которая выдает РО',guild_ids=[common.guild_id])
    @common.commands.has_any_role('Создатель','Тех. Администратор','Администратор')
    async def ro(self, ctx, member: common.discord.Member, duration:str, reason: str):
        role = common.discord.utils.get(ctx.guild.roles, name='READ ONLY')
        print(role)
        embed = common.discord.Embed(title='Наказание!', color=common.discord.Color.red())
        # Give the user the specified role
        if member:
            try:
                await member.add_roles(role)
            except RuntimeError:
                print("Member was not found")
        
        
        # Calculate the time when the role should be removed
        duration_value = int(duration[:-1])  # Extract numeric value
        duration_unit = duration[-1] 
        removal_time = -1
        if duration_unit == 'h': 
            removal_time = common.datetime.datetime.utcnow() + common.datetime.timedelta(hours=duration_value)
        elif duration_unit == 'd':
            removal_time = common.datetime.datetime.utcnow() + common.datetime.timedelta(days=duration_value)


        # Schedule a task to remove the role after 'duration' days
        task = self.bot.loop.create_task(self.remove_role_after(member, role, removal_time))
        self.scheduled_tasks[member.id] = task
        embed.add_field(name="Кем выдано",value=ctx.author.mention)
        embed.add_field(name="Наказание", value=f"{member.mention} вам была выдана роль: {role.mention} на {duration}", inline=False)
        embed.add_field(name='Причина', value = reason)
        await ctx.respond(member.mention,embed = embed)

    async def remove_role_after(self, member, role, duration):
        # Extract the duration value and unit from the provided string
        duration_value = int(duration[:-1])  # Extract numeric value
        duration_unit = duration[-1]          # Extract duration unit (d for days, h for hours)

        # Calculate the timedelta based on the duration unit
        if duration_unit == 'd':
            removal_time = datetime.datetime.utcnow() + datetime.timedelta(days=duration_value)
        elif duration_unit == 'h':
            removal_time = datetime.datetime.utcnow() + datetime.timedelta(hours=duration_value)
        else:
            raise ValueError("Invalid duration format. Please use '<n>d' for days or '<n>h' for hours.")

        # Wait until the removal time
        await asyncio.sleep((removal_time - datetime.datetime.utcnow()).total_seconds())
        
        # Remove the role
        await member.remove_roles(role)
    
    @common.commands.slash_command(name="poll", description="команда для создания системы голосований")
    async def poll(ctx, question, *options: str):
        if len(options) <= 1:
            await ctx.send("Система должна иметь больше одной опции!")
            return
        if len(options) > 3:
            await ctx.send("Система не должна иметь больше чем 3 опции!")
            return
        
        # Create the poll message
        embed = common.discord.Embed(title="Голосование", description=question, color=0x00ff00)
        fields = [("Опции", "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)]), False),
                ("Инструкции", "Поставьте реакцию чтобы проголосовать", False)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        
        poll_message = await ctx.send(embed=embed)  
        active_polls.add(poll_message.id)# Sending the poll message
        for emoji in (u"\U00000031\U0000FE0F\U000020E3", u"\U00000032\U0000FE0F\U000020E3", u"\U00000033\U0000FE0F\U000020E3", 
                    u"\U00000034\U0000FE0F\U000020E3", u"\U00000035\U0000FE0F\U000020E3", u"\U00000036\U0000FE0F\U000020E3", 
                    u"\U00000037\U0000FE0F\U000020E3", u"\U00000038\U0000FE0F\U000020E3", u"\U00000039\U0000FE0F\U000020E3", 
                    u"\U00000030\U0000FE0F\U000020E3")[:len(options)]:
            await poll_message.add_reaction(emoji)  # Add reactions for voting


    @common.bot.event
    async def on_reaction_add(reaction, user):
        if user == common.bot.user:
            return
        if reaction.message.id not in active_polls:
            return  # Only process reactions on active polls
        

def setup(bot):
    bot.add_cog(Administrative(bot))
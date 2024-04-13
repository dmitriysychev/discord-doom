import common
from discord.ui import View, Select
import asyncio
import sqlite3
import json

# class Tickets(common.commands.Cog):
all_admin_roles = ['Создатель','Тех. Администратор','Администратор','Модератор','Ст. РП Куратор']
MODERATOR_ID = 1009677024819937371
    # def __init__(self, bot):
    #     self.bot = bot


            
class OpenView(common.discord.ui.View): # Create a class called MyView that subclasses common.discord.ui.View
    CAT_ADM_COMPLAINS = 1010800079789105182
    CAT_UNBAN = 1010808324742193182
    CAT_PLR_COMPLAINS = 1010796625473568798
    CAT_RETURNS = 1010786296995795014
    CAT_TEAM = 1016401128377823232

    def __init__(self, close_view_cls, disable_on_timeout=True):
        super().__init__(timeout=None, disable_on_timeout=True)
        self.close_view_cls = close_view_cls

    @common.discord.ui.select( # the decorator that lets you specify the properties of the select menu
    placeholder = "Категории тикетов", # the placeholder text that will be displayed if nothing is selected
    min_values = 1, # the minimum number of values that must be selected by the users
    max_values = 1, # the maximum number of values that can be selected by the users
    custom_id = "selectPreview",
    options = [ # the list of options from which users can choose, a required field
        common.discord.SelectOption(
            label="│Заявка в О-Сознание",
            emoji="📮",
            description="Категория чтобы подать заявку на администрацию проекта"
        ),
        common.discord.SelectOption(
            label="│Жалоба на игрока",
            emoji="⛳",
            description="Категория для жалоб на игроков"
        ),
        common.discord.SelectOption(
            label="│Жалоба на администрацию",
            emoji="🎫",
            description="Категория чтобы подать жалобу на администрацию"
        ),
        common.discord.SelectOption(
            label="│Возврат вещей",
            emoji="🌌",
            description="Категория чтобы подать заявку на возврат вещей"
        ),
        common.discord.SelectOption(
            label="│Заявка на разбан",
            emoji="🌠",
            description="Категория чтобы подать заявку на разбан в игре"
        )
    ]
    )
    async def select_callback(self, select, interaction): # the function called when the user is done selecting options
        #await interaction.response.send_message(f"Спасибо что выбрали {select.values[0]}")
        '''
        Жалобы на администрацию = 1010800079789105182
        Заявки на разбан = 1010808324742193182
        Жалобы на игроков = 1010796625473568798
        Возврат вещей = 1010786296995795014
        Заявки в команду = 1016401128377823232
        '''
        ctx = interaction.channel
        category_id = 1010960851362140171#placeholder
        if select.values[0] in "│Заявка в О-Сознание":
            category_id = self.CAT_TEAM
        elif  select.values[0] in "│Жалоба на игрока":
            category_id = self.CAT_PLR_COMPLAINS
        elif  select.values[0] in "│Жалоба на администрацию":
            category_id = self.CAT_ADM_COMPLAINS
        elif  select.values[0] in "│Возврат вещей":
            category_id = self.CAT_RETURNS
        elif  select.values[0] in "│Заявка на разбан":
            category_id = self.CAT_UNBAN
        category = ctx.guild.get_channel(category_id)
        if category:
            ticket_channel = await category.create_text_channel(name=f'ticket-{interaction.user.name}')

            await ticket_channel.set_permissions(ctx.guild.default_role, view_channel=False)
            await ticket_channel.set_permissions(interaction.user, view_channel=True, read_messages=True, send_messages=True)
            
            embed = common.discord.Embed(title='Что у вас случилось?', description='Кратко опишите проблему чтобы мы могли вам помочь.\nТегните роль того кто вам нужен.', color=common.discord.Color.green())
            embed.set_footer(text="DOOM DAYz S.T.A.L.K.E.R RP", icon_url="https://i.imgur.com/2aGxDZe.png")
            
            await ticket_channel.send(interaction.user.mention)
            await ticket_channel.send(embed=embed, view=self.close_view_cls())
            

            await interaction.response.send_message(f"Тикет создан! Найти его можно тут -> {ticket_channel.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message("Не могу найти категорию")


class CloseView(common.discord.ui.View):
    def __init__(self, disable_on_timeout=True):
        super().__init__(timeout=None, disable_on_timeout=True)
        #self.ticket_channel = ticket_channel
        #dynamically creating the Buttons for the message depending in the list.
    async def on_timeout(self):
        super().on_timeout(self)
        print('VIEW HAS TIMED OUT')
        pass

    @common.discord.ui.button(label="Закрыть тикет", style=common.discord.ButtonStyle.danger, custom_id="closeview:Danger") # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        # Check if the user has permission to close the ticket (only the ticket author should have permission)
        button_id = button.custom_id
        print(f"Received button click: {button_id}") #Print for the msg ID
        #if interaction.channel.name.startswith('ticket-'):
        # Check if the author of the message is the ticket creator
        member_roles = [role.name for role in interaction.user.roles]
        allow =  any(role in all_admin_roles for role in member_roles)
        if interaction.channel.name[len('ticket-'):] == interaction.user or allow:
            await interaction.response.send_message("Вы уверены что хотите закрыть тикет?", view=MakeSureView())

        else:
            await interaction.response.send_message("Вы можете закрывать только свои тикеты")

class MakeSureView(common.discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, disable_on_timeout=True)
        self.yes_button = common.discord.ui.Button(style=common.discord.ButtonStyle.green, label="Да", custom_id="closeview:Yes")
        self.yes_button.callback = self.on_yes_button_click
        self.add_item(self.yes_button)

         # Button 3: Наверное (Maybe)
        self.maybe_button = common.discord.ui.Button(style=common.discord.ButtonStyle.primary, label="Не Знаю", custom_id="closeview:Maybe")
        self.maybe_button.callback = self.on_maybe_button_click
        self.add_item(self.maybe_button)

        # Button 2: Нет (No)
        self.no_button = common.discord.ui.Button(style=common.discord.ButtonStyle.red, label="Нет", custom_id="closeview:No")
        self.no_button.callback = self.on_no_button_click
        self.add_item(self.no_button)

       

    async def on_yes_button_click(self, interaction: common.discord.Interaction):
        user = interaction.user
        channel = interaction.channel
        member_roles = [role.name for role in interaction.user.roles]
        allow =  any(role in all_admin_roles for role in member_roles)
        if interaction.channel.name[len('ticket-'):] == interaction.user or allow:
            await interaction.response.send_message("Тикет будет закрыт через 15 секнуд")
            await asyncio.sleep(15)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("Вы можете закрывать только свои тикеты")

    async def on_no_button_click(self, interaction: common.discord.Interaction):
        await interaction.response.defer()
        user = interaction.user
        channel = interaction.channel
        await interaction.message.delete()

    async def on_maybe_button_click(self, interaction: common.discord.Interaction):
        user = interaction.user
        role = common.discord.utils.get(user.guild.roles, id=MODERATOR_ID)
        await interaction.response.send_message(f"{role.mention} Помогите человеку с тикетом")
        self.maybe_button.disabled = True
        await interaction.message.edit(view=self)

class TicketCog(common.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @common.commands.Cog.listener()
    async def on_ready(self):
        view = OpenView(CloseView)
        viewClosed = CloseView()
        viewMaybe = MakeSureView()
        self.bot.add_view(view)
        self.bot.add_view(viewClosed)
        self.bot.add_view(viewMaybe)

    @common.commands.slash_command(name='ticket', description='Creates a ticket form',guild_ids=[common.guild_id])
    async def ticket(self,ctx):
        # Create an instance of the OpenView class and pass the view state
        embed = common.discord.Embed(title='Чем мы можем помочь?', description="Выберете категорию тикета который хотите открыть.", color=common.discord.Color.gold())
        embed.set_footer(text="Команда DOOM DAYz S.T.A.L.K.E.R RP", icon_url="https://i.imgur.com/2aGxDZe.png")
        await ctx.send(embed=embed, view=OpenView(CloseView))

    

async def setup(bot):
    await bot.add_cog(TicketCog(bot))


    
import common 
import requests
import asyncio
pda_webhook_url = "https://discord.com/api/webhooks/1228178493255192597/Z5RU4qj8zPXO2P9HmlbJv1dVID2iEXGM1jo5zcq8Tx0dPLjjawJmIiYnw1a_4piPEfZw"#"https://discord.com/api/webhooks/1228145150836867103/XVZ2lpirzGOA3D9yXqyVxgS-4AluAPVJ_VKhQwW4JJK6wNebne-45aLzUsWCWddOlVRi"
pda_headers = {
    'X-RapidAPI-Key': '491ce3edf8msh10db694d3787c7fp146ebajsn6a823d2c4b3f',
    'X-RapidAPI-Host': 'discord-webhook-api.p.rapidapi.com'
  }


class RapiAPI(common.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @common.commands.slash_command(name='send_message', description='Команда которая может отправлять сообщения от имени бота',guild_ids=[common.guild_id])
    async def send_message(self, ctx, msg):
        params = {"webhook_url": pda_webhook_url, "message": msg}
        self.pda("send_message", params=params)
        await ctx.response.send_message('Сообщение кпк отправлено', ephemeral=True)

    @common.commands.slash_command(name='send_message_repeat', description='Команда которая может отправлять сообщения от имени бота',guild_ids=[common.guild_id])
    @common.commands.has_any_role('Создатель','Тех. Администратор','Администратор')
    async def send_message_repeat(self, ctx, msg: str, count: int):
        params = {"webhook_url": pda_webhook_url, "message": msg, "repeat":count}
        self.pda("repeat_send_message", params=params)
        await ctx.response.send_message('Отправлено', ephemeral=True)



    @common.commands.slash_command(name='tt', description='Команда которая чистит количество сообщений',guild_ids=[common.guild_id])
    async def tt(self, interaction, content):
        await interaction.response.send_message("Reply")
    def pda(self, uri, params):
        requests.get(f"https://discord-webhook-api.p.rapidapi.com/{uri}", headers=pda_headers, params=params)

def setup(bot):
    bot.add_cog(RapiAPI(bot))

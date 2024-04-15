import common
import asyncio
import datetime
from discord.ui import View, Button

        
class EndPollButton(common.discord.ui.Button):
    def __init__(self, message):
        super().__init__(style=common.discord.ButtonStyle.red, label="Закрыть голосование")
        self.message = message

    async def callback(self, interaction):
        if self.view:
            self.view.stop()
        await end_poll(self.message, interaction.channel, early=True)

async def end_poll(message, channel, early=False):
    # Disable the button after use
    for item in message.components:
        for button in item.children:
            button.disabled = True
    try:
        if message.components:
            await message.edit(components=[common.discord.ActionRow(*message.components[0].children)])
        else:
            # Maybe log this situation or alert yourself that no components were found
            print("No components available to edit.")
    except IndexError as e:
        print(f"Error accessing components: {e}")

    # Count the votes
    message = await channel.fetch_message(message.id)  # Refresh the message to get all reactions
    results = {}
    for reaction in message.reactions:
        results[reaction.emoji] = reaction.count - 1  # subtract one to exclude the bot's own reaction

    # Create and send the result embed
    description = "\n".join([f"Количестов за опцию {key}: {val} " for key, val in results.items()])
    embed = common.discord.Embed(title="Результаты голосования", description=description, color=0x00ff00)
    await channel.send(embed=embed)

    if early:
        await channel.send("Голосование было закончено раньше")

class PollCog(common.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @common.commands.Cog.listener()
    async def on_ready(self):
       pass

    @common.commands.slash_command(name='poll', description='Команда которая выдает создает голосование',guild_ids=[common.guild_id])
    async def poll(self,ctx, question, option1: str, option2: str, option3: str = None, option4: str = None, option5:str = None):
        options = [opt for opt in [option1, option2, option3, option4, option5] if opt is not None]
        if len(options) < 2:
            await ctx.reply("Нужно как минимум два варианта ответа")
            return

        embed = common.discord.Embed(title="Голосование", description=question, color=0x00ff00)
        embed.add_field(name="Варианты ответов:", value="\n".join([f"{i+1}. {option}" for i, option in enumerate(options)]), inline=False)
        poll_message = await ctx.send(embed=embed)
        
        for i in range(len(options)):
            await poll_message.add_reaction(emoji=str(i+1)+u"\ufe0f\u20e3")
        await ctx.respond("Голосование открыто!", ephemeral=True)
        button = EndPollButton(poll_message)
        view = View()
        view.add_item(button)
        await poll_message.edit(view=view)

        # Setup timer for the poll duration
        await asyncio.sleep(600)  # Wait for 10 minutes
        if not button.view.is_finished():
            await end_poll(poll_message, ctx.channel)

def setup(bot):
    bot.add_cog(PollCog(bot))
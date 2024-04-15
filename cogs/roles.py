import common
import asyncio
"""
Let users assign themselves roles by clicking on Buttons.
The view made is persistent, so it will work even when the bot restarts.

See this example for more information about persistent views:
https://github.com/Pycord-Development/pycord/blob/master/examples/views/persistent.py
Make sure to load this cog when your bot starts!
"""

# This is the list of role IDs that will be added as buttons.
role_ids = [1019404287526305812,1017927971572559903,1019402335170076772,1009686240074932305]


class RoleButton(common.discord.ui.Button):
    def __init__(self):
        """A button for one role. `custom_id` is needed for persistent views."""
        super().__init__(
            label="Войти в Зону",
            style=common.discord.ButtonStyle.danger,
            custom_id="enterzone",
            emoji="☢️",
            row=2
        )

    async def callback(self, interaction: common.discord.Interaction):
        """
        This function will be called any time a user clicks on this button.

        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction object that was created when a user clicks on a button.
        """
        try:
        # Get the user who clicked the button.
            user =  interaction.user
            # # Get the role this button is for (stored in the custom ID).
            success = False
            for single_role in role_ids:
                role = interaction.guild.get_role(single_role)
                # Add the role and send a response to the user ephemerally (hidden to other users).
                if role not in user.roles:
                    # Give the user the role if they don't already have it.
                    await user.add_roles(role)
                    success = True
                else:
                    success = False
                    
                    await interaction.response.send_message(f"У вас уже есть все роли зоны.",ephemeral=True,)
                    
            if success:
                await interaction.response.send_message(
                        f"Добро пожаловать, Сталкер!",
                        ephemeral=True,)
        except:
            pass

class ButtonRoleCog(common.commands.Cog):
    """
    A cog with a slash command for posting the message with buttons
    and to initialize the view again when the bot is restarted.
    """

    def __init__(self, bot):
        self.bot = bot

    # Pass a list of guild IDs to restrict usage to the supplied guild IDs.
    @common.commands.slash_command(name='post',guild_ids=[common.guild_id], description="Post the button role message")
    async def post(self, ctx: common.discord.ApplicationContext):
        """Slash command to post a new view with a button for each role."""

        # timeout is None because we want this view to be persistent.
        view = common.discord.ui.View(timeout=None)

        view.add_item(RoleButton())
        embed = common.discord.Embed(title='Получение роли', description="После прочтения ЛОРа свервера 👇", color=common.discord.Color.red())
        embed.set_footer(text="Команда DOOM DAYz S.T.A.L.K.E.R RP", icon_url="https://i.imgur.com/2aGxDZe.png")
        await ctx.send(embed=embed, view=view)
        
    @common.commands.Cog.listener()
    async def on_ready(self):
        """
        This method is called every time the bot restarts.
        If a view was already created before (with the same custom IDs for buttons),
        it will be loaded and the bot will start watching for button clicks again.
        """
        # We recreate the view as we did in the /post command.
        view = common.discord.ui.View(timeout=None)
        # Make sure to set the guild ID here to whatever server you want the buttons in!
        guild = self.bot.get_guild(1009672589825814529)
        view.add_item(RoleButton())

        # Add the view to the bot so that it will watch for button interactions.
        self.bot.add_view(view)


def setup(bot):
    bot.add_cog(ButtonRoleCog(bot))

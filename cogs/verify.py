from discord.ext import commands

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def verify(self, ctx, link: str = None):
        if link is None:
            await ctx.send("Du skal sende et link, fx: `!verify https://www.op.gg/summoners/euw/Navn`")
        else:
            await ctx.send(f"Jeg fik dit link: {link}")

async def setup(bot):
    await bot.add_cog(Verify(bot))
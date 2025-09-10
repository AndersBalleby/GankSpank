import os
from discord.ext import commands
from urllib.parse import unquote
from riotwatcher import LolWatcher, RiotWatcher, ApiError
from utils.roles import get_highest_tier, ensure_rank_roles, assign_rank_role

lol_watcher = LolWatcher(os.getenv("RIOT_API_KEY"))

riot_watcher = RiotWatcher(os.getenv("RIOT_API_KEY"))

# Region map (OP.GG -> Riot API)
region_map = {
    "euw": "euw1",
    "eune": "eun1",
    "na": "na1",
    "kr": "kr",
    "lan": "la1",
    "las": "la2",
    "oce": "oc1",
    "tr": "tr1",
    "ru": "ru",
    "jp": "jp1",
    "br": "br1"
}

#Verification channel
RESULTS_CHANNEL_ID = 1415301899200237679

def parse_opgg_link(link: str):
    """Extractor region og summoner navn fra et OP.GG link"""
    try:
        parts = link.split("/")
        region = parts[-2]
        summoner_name = parts[-1].split("-")[0]
        summoner_tag = parts[-1].split("-")[1]
        return region, summoner_name, summoner_tag
    except Exception:
        return None, None, None



def fetch_ranks(region: str, summoner_name: str, summoner_tag: str):
    """Fetcher ranked stats fra Riot API"""
    if region not in region_map:
        return None, f"Region '{region}' understøttes ikke."

    try:
        fetched_account = riot_watcher.account.by_riot_id("EUROPE", summoner_name, summoner_tag)
        api_region = region_map[region]

        fetched_user = lol_watcher.summoner.by_puuid(api_region, fetched_account["puuid"])
        ranked_stats = lol_watcher.league.by_puuid(api_region, fetched_user["puuid"])

        return ranked_stats, None
    except ApiError as e:
        return None, f"API fejl: {e}"


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Sørg for at roller eksisterer, når botten starter
        for guild in self.bot.guilds:
            await ensure_rank_roles(guild)

    @commands.command()
    async def verify(self, ctx, link: str = None):
        # Slet brugerens besked
        try:
            await ctx.message.delete()
        except Exception:
            pass  # Hvis botten ikke har permission, ignorere

        if link is None:
            await ctx.send("Du skal sende et link, fx: `!verify https://www.op.gg/summoners/euw/Navn-Tag`")
            return

        region, summoner_name, summoner_tag = parse_opgg_link(link)
        if not region or not summoner_name or not summoner_tag:
            await ctx.send("Kunne ikke parse linket.")
            return

        ranked_stats, error = fetch_ranks(region, summoner_name, summoner_tag)
        if error:
            await ctx.send(error)
            return

        if not ranked_stats:
            await ctx.send(f"{summoner_name} har ingen ranked data.")
            return

        # Ranked stats tekst
        results = [f"**{unquote(summoner_name)}** - ranked stats:"]
        for queue in ranked_stats:
            queue_type = queue["queueType"].replace("_", " ").title()
            tier = queue["tier"]
            rank = queue["rank"]
            lp = queue["leaguePoints"]
            results.append(f"{queue_type}: {tier} {rank} ({lp} LP)")

        #Skifter til verification channel
        channel = self.bot.get_channel(RESULTS_CHANNEL_ID)
        if channel is None:
            await ctx.send("Resultatkanalen findes ikke, tjek ID.")
            return

        # Post resultater i verification channel
        await channel.send("\n".join(results))
        
        #Rolle tildeling
        highest_tier = get_highest_tier(ranked_stats)
        if highest_tier:
            role = await assign_rank_role(ctx.author, highest_tier)
            if role:
                await channel.send(f"{ctx.author.mention}, du har fået rollen **{role.name}**!")


async def setup(bot):
    await bot.add_cog(Verify(bot))

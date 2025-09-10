import os
from discord.ext import commands
from urllib.parse import unquote
from riotwatcher import LolWatcher, RiotWatcher, ApiError

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


def parse_opgg_link(link: str):
    """Extractor region og summoner navn fra et OP.GG link"""
    try:
        parts = link.split("/")
        region = parts[-2]
        summoner_name = parts[-1].split("-")[0]
        summoner_tag = parts[-1].split("-")[1]
        return region, summoner_name, summoner_tag
    except Exception:
        return None, None


def get_ranks_from_opgg(link: str):
    region, summoner_name, summoner_tag = parse_opgg_link(link)
    if not region or not summoner_name:
        return "Kunne ikke parse linket."

    if region not in region_map:
        return f"Region '{region}' understøttes ikke."
    
    fetched_account = riot_watcher.account.by_riot_id('EUROPE', summoner_name, summoner_tag)
    api_region = region_map[region]

    fetched_user = lol_watcher.summoner.by_puuid(api_region, fetched_account['puuid'])

    try:
        ranked_stats = lol_watcher.league.by_puuid(api_region, fetched_user['puuid'])

        if not ranked_stats:
            return f"{summoner_name} har ingen ranked data."

        results = [f"**{unquote(summoner_name)}** - ranked stats:"]
        for queue in ranked_stats:
            queue_type = queue["queueType"].replace("_", " ").title()
            tier = queue["tier"]
            rank = queue["rank"]
            lp = queue["leaguePoints"]
            results.append(f"{queue_type}: {tier} {rank} ({lp} LP)")

        return "\n".join(results)

    except ApiError as e:
        return f"API fejl: {e}"


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def verify(self, ctx, link: str = None):
        # Slet brugerens besked
        try:
            await ctx.message.delete()
        except Exception:
            pass  # Hvis botten ikke har permission, ignorerer vi det
        if link is None:
            await ctx.send("Du skal sende et link, fx: `!verify https://www.op.gg/summoners/euw/Navn`")
            return

        result = get_ranks_from_opgg(link)
        await ctx.send(result)


async def setup(bot):
    await bot.add_cog(Verify(bot))

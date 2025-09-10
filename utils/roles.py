import discord

rank_colors = {
    "Iron": 0x6d6d6d,
    "Bronze": 0x8c6a43,
    "Silver": 0xb5b5b5,
    "Gold": 0xffd700,
    "Platinum": 0x00b0b9,
    "Emerald": 0x50C878,
    "Diamond": 0x5865f2,
    "Master": 0xa020f0,
    "Grandmaster": 0xff3030,
    "Challenger": 0x00ffff
}
tier_order = [
    "IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD",
    "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"
]


def get_highest_tier(ranked_stats):
    """Find spillerens højeste tier ud fra Riot API data"""
    if not ranked_stats:
        return None
    ranked_stats.sort(key=lambda x: tier_order.index(x["tier"]))
    return ranked_stats[-1]["tier"].title()


async def ensure_rank_roles(guild):
    """Sørg for at alle rank-roller eksisterer på serveren"""
    for rank, color in rank_colors.items():
        role = discord.utils.get(guild.roles, name=rank)
        if not role:
            await guild.create_role(name=rank, colour=discord.Colour(color))


async def assign_rank_role(member: discord.Member, highest_tier: str):
    """Tildel rolle til en spiller baseret på deres højeste tier"""
    if not highest_tier:
        return

    # Fjern gamle rank-roller først (hvis de har en)
    for role in member.roles:
        if role.name in rank_colors.keys():
            await member.remove_roles(role)

    # Find eller opret rollen
    role = discord.utils.get(member.guild.roles, name=highest_tier)
    if not role:
        role = await member.guild.create_role(
            name=highest_tier,
            colour=discord.Colour(rank_colors.get(highest_tier, 0xffffff))
        )

    await member.add_roles(role)
    return role

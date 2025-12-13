import os
import discord
from utils.db import fetch_voyages, get_active_season
from utils.format_number import format_number


def calculate_ranking(season):
    from collections import defaultdict

    voyages = fetch_voyages(season)

    ranking = defaultdict(int)

    for voyage in voyages:
        for uid in voyage['members']:
            ranking[uid] += voyage.get('gold', 0)

    return dict(sorted(ranking.items(), key=lambda x: x[1], reverse=True))

def format_ranking(guild, ranking, season, title=None):
    if not title:
        title = f"# 🏆 Classement des Rats du Large - {season} #"

    lines = [title]

    for idx, (uid, amount) in enumerate(ranking.items(), start=1):
        user = guild.get_member(uid)
        name = user.display_name if user else f"<@{uid}>"
        lines.append(f"{idx}. {name}: {format_number(amount)} gold")

    return "\n".join(lines)

async def update_ranking(interaction: discord.Interaction):
    # Vérifier qu'une saison est active
    active_season = get_active_season()
    if not active_season:
        # Si aucune saison active, ne pas faire d'erreur mais ne rien faire
        return
    
    season_name = active_season['name']
    ranking = calculate_ranking(season_name)
    message = format_ranking(interaction.guild, ranking, season_name)

    ranking_channel = interaction.guild.get_thread(int(os.getenv('RANKING_CHANNEL_ID'))) or interaction.guild.get_channel(int(os.getenv('RANKING_CHANNEL_ID')))

    if ranking_channel:
        async for msg in ranking_channel.history(limit=50):
            if msg.author == interaction.client.user:
                await msg.edit(content=message)
                break
        else:
            await ranking_channel.send(message)
    else:
        await interaction.channel.send(message)
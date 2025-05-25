import os
import discord
from utils.db import fetch_voyages
from utils.format_number import format_number


def calculate_ranking(season):
    from collections import defaultdict

    voyages = fetch_voyages(season)

    ranking = defaultdict(int)

    for voyage in voyages:
        for uid in voyage['members']:
            ranking[uid] += voyage.get('emissary_value', 0)

    return dict(sorted(ranking.items(), key=lambda x: x[1], reverse=True))

def format_ranking(guild, ranking, season, title=None):
    if not title:
        title = f"# 🏆 Classement des Rats du Large - {season} #"

    lines = [title]

    for idx, (uid, amount) in enumerate(ranking.items(), start=1):
        user = guild.get_member(uid)
        name = user.display_name if user else f"<@{uid}>"
        lines.append(f"{idx}. {name}: {format_number(amount)} valeur d'émissaire")

    return "\n".join(lines)

async def update_ranking(interaction: discord.Interaction):
    season = interaction.channel.name
    ranking = calculate_ranking(season)
    message = format_ranking(interaction.guild, ranking, season)

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
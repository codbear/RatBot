# slash_commands/stats.py
import discord
from discord import app_commands
from datetime import datetime, timedelta
from core.bot import tree
from utils.db import fetch_voyages, get_active_season, get_all_seasons
from utils.send import send_ephemeral_message
from utils.format_number import format_number

statsCmd = app_commands.Group(name="stats", description="Statistiques des voyages et saisons")

@statsCmd.command(name="saison", description="Statistiques détaillées de la saison en cours")
async def season_stats(interaction: discord.Interaction):
    """Affiche les statistiques de la saison actuelle."""
    
    active_season = get_active_season()
    if not active_season:
        return await send_ephemeral_message(interaction, "❌ Aucune saison n'est active.")
    
    season_name = active_season['name']
    voyages = fetch_voyages(season_name)
    
    if not voyages:
        return await send_ephemeral_message(interaction, f"📊 Aucun voyage enregistré pour la saison **{season_name}**.")
    
    # Calculs des statistiques
    total_voyages = len(voyages)
    total_gold = sum(v['gold'] for v in voyages)
    total_emissary = sum(v['emissary_value'] for v in voyages)
    total_days = sum(v['duration'] for v in voyages)
    
    # Participants uniques
    unique_participants = set()
    for voyage in voyages:
        unique_participants.update(voyage['members'])
    
    # Moyennes
    avg_gold_per_voyage = total_gold / total_voyages if total_voyages > 0 else 0
    avg_emissary_per_voyage = total_emissary / total_voyages if total_voyages > 0 else 0
    avg_duration = total_days / total_voyages if total_voyages > 0 else 0
    
    # Embed
    embed = discord.Embed(
        title=f"📊 Statistiques - {season_name}",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    # Statistiques générales
    embed.add_field(
        name="🚢 Voyages",
        value=f"**{total_voyages}** voyages\n⏱️ **{total_days}** jours total\n👥 **{len(unique_participants)}** participants",
        inline=True
    )
    
    embed.add_field(
        name="🪙 Butin total",
        value=f"**{format_number(total_gold)}** or\n🏆 **{format_number(total_emissary)}** émissaire",
        inline=True
    )
    
    embed.add_field(
        name="📈 Moyennes",
        value=f"🪙 **{format_number(int(avg_gold_per_voyage))}** or/voyage\n🏆 **{format_number(int(avg_emissary_per_voyage))}** émiss./voyage\n⏱️ **{avg_duration:.1f}** jours/voyage",
        inline=True
    )
    
    # Top 3 des voyages les plus lucratifs
    top_voyages = sorted(voyages, key=lambda x: x['gold'], reverse=True)[:3]
    if top_voyages:
        top_text = []
        for i, voyage in enumerate(top_voyages, 1):
            members_mentions = ', '.join(f"<@{uid}>" for uid in voyage['members'][:2])
            if len(voyage['members']) > 2:
                members_mentions += f" +{len(voyage['members']) - 2}"
            top_text.append(f"**{i}.** {format_number(voyage['gold'])} or - {members_mentions}")
        
        embed.add_field(
            name="🏆 Top 3 voyages",
            value='\n'.join(top_text),
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@statsCmd.command(name="joueur", description="Statistiques d'un joueur pour la saison en cours")
@app_commands.describe(membre="Membre dont voir les statistiques (optionnel, par défaut vous-même)")
async def player_stats(interaction: discord.Interaction, membre: discord.Member = None):
    """Affiche les statistiques d'un joueur pour la saison actuelle."""
    
    target_user = membre or interaction.user
    
    active_season = get_active_season()
    if not active_season:
        return await send_ephemeral_message(interaction, "❌ Aucune saison n'est active.")
    
    season_name = active_season['name']
    voyages = fetch_voyages(season_name)
    
    # Filtrer les voyages du joueur
    player_voyages = [v for v in voyages if target_user.id in v['members']]
    
    if not player_voyages:
        name = "vous" if target_user == interaction.user else target_user.display_name
        return await send_ephemeral_message(
            interaction, 
            f"📊 {name.capitalize()} n'avez effectué aucun voyage cette saison."
        )
    
    # Calculs
    total_voyages = len(player_voyages)
    total_gold = sum(v['gold'] for v in player_voyages)
    total_emissary = sum(v['emissary_value'] for v in player_voyages)
    total_days = sum(v['duration'] for v in player_voyages)
    
    # Moyennes
    avg_gold = total_gold / total_voyages
    avg_emissary = total_emissary / total_voyages
    avg_duration = total_days / total_voyages
    
    # Embed
    embed = discord.Embed(
        title=f"📊 Statistiques de {target_user.display_name}",
        description=f"Saison : **{season_name}**",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    
    embed.set_thumbnail(url=target_user.display_avatar.url)
    
    embed.add_field(
        name="🚢 Participation",
        value=f"**{total_voyages}** voyages\n**{total_days}** jours en mer",
        inline=True
    )
    
    embed.add_field(
        name="🪙 Gains totaux",
        value=f"**{format_number(total_gold)}** pièces d'or\n**{format_number(total_emissary)}** émissaire",
        inline=True
    )
    
    embed.add_field(
        name="📈 Moyennes",
        value=f"🪙 **{format_number(int(avg_gold))}** or/voyage\n🏆 **{format_number(int(avg_emissary))}** émiss./voyage\n⏱️ **{avg_duration:.1f}** jours/voyage",
        inline=False
    )
    
    # Meilleur voyage
    best_voyage = max(player_voyages, key=lambda x: x['gold'])
    embed.add_field(
        name="🏆 Meilleur voyage",
        value=f"**Voyage n°{best_voyage['id']}**\n🪙 {format_number(best_voyage['gold'])} or\n⏱️ {best_voyage['duration']} jours",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

tree.add_command(statsCmd)
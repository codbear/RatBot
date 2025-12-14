# commands/ranking.py
import discord
from core.bot import tree
from utils.db import fetch_voyages, get_active_season
from utils.send import send_ephemeral_message
from utils.ranking import calculate_ranking, update_ranking, format_user_ranking_position

rankingCmd = discord.app_commands.Group(name="classement", description="Commandes liées au classement des Rats du Large")

@rankingCmd.command(name="personnel", description="Affiche ta position dans le classement actuel de la saison")
async def rankingSelf(interaction: discord.Interaction):
    # Vérifier qu'une saison est active
    active_season = get_active_season()
    if not active_season:
        return await send_ephemeral_message(
            interaction, 
            "❌ Aucune saison n'est active. Impossible d'afficher le classement."
        )
    
    season_name = active_season['name']
    ranking = calculate_ranking(season_name)

    if not ranking:
        await send_ephemeral_message(interaction, f"Aucune donnée enregistrée pour la {season_name}")
        return

    ranking_list = list(ranking.items())
    position = next((i + 1 for i, (uid, _) in enumerate(ranking_list) if uid == interaction.user.id), None)

    if position:
        await send_ephemeral_message(interaction, f"🔍 Tu es en **{position}e position** pour la **{season_name}**.")
    else:
        await send_ephemeral_message(interaction, "😕 Tu n'es pas encore classé dans cette saison.")

@rankingCmd.command(name="inactifs", description="Affiche la liste des membres inactifs lors de la saison")
async def inactifs(interaction: discord.Interaction):
    # Vérifier qu'une saison est active
    active_season = get_active_season()
    if not active_season:
        return await send_ephemeral_message(
            interaction, 
            "❌ Aucune saison n'est active. Impossible d'afficher les inactifs."
        )
    
    season_name = active_season['name']
    voyages = fetch_voyages(season_name)
    ranking = calculate_ranking(season_name)

    if not ranking:
        await send_ephemeral_message(interaction, f"Aucune donnée enregistrée pour la {season_name}")
        return
    
    role = discord.utils.get(interaction.guild.roles, name="Rat du large")

    if not role:
        return await send_ephemeral_message(interaction, "Le rôle 'Rat du large' est introuvable.")
        
    guild_members = {m.id for m in role.members if not m.bot}
    participants = {uid for s in voyages if s['season'] == season_name for uid in s['members']}
    inactifs_ids = guild_members - participants
    ranking = {uid: 0 for uid in inactifs_ids}

    lines = [f"# 📜 Membres inactifs pendant la {season_name} #"]

    for uid in inactifs_ids:
        user = interaction.guild.get_member(uid)
        name = user.display_name if user else f"<@{uid}>"
        lines.append(f"- {name}")

    message = "\n".join(lines)

    await send_ephemeral_message(interaction, message)

@rankingCmd.command(name="update", description="Mettre à jour le classement de la saison")
async def rankingUpdate(interaction: discord.Interaction):
    await update_ranking(interaction)
    await send_ephemeral_message(interaction, "✅ Le classement a été mis à jour avec succès.")

tree.add_command(rankingCmd)

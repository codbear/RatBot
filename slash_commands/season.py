# slash_commands/season.py
import discord
from discord import app_commands
from datetime import datetime
from core.bot import tree
from utils.check_role import is_admin
from utils.send import send_ephemeral_message
from utils.db import start_season, end_current_season, get_active_season, get_all_seasons

seasonCmd = app_commands.Group(name="saison", description="Commandes pour gérer les saisons")

@seasonCmd.command(name="demarrer", description="Commencer une nouvelle saison")
@app_commands.describe(nom="Nom de la nouvelle saison")
async def start_new_season(interaction: discord.Interaction, nom: str):
    """Démarre une nouvelle saison de guilde."""
    if not is_admin(interaction):
        return await send_ephemeral_message(interaction, "❌ Seul un chef de guilde peut démarrer une nouvelle saison.")

    # Vérifier s'il y a déjà une saison active
    current_season = get_active_season()
    if current_season:
        return await send_ephemeral_message(
            interaction, 
            f"❌ Une saison est déjà en cours : **{current_season['name']}**\n"
            f"Utilisez `/saison terminer` d'abord pour la terminer."
        )

    try:
        # Créer la nouvelle saison
        season_id = start_season(nom)
        
        embed = discord.Embed(
            title="🎉 Nouvelle saison démarrée !",
            description=f"**{nom}** (ID: {season_id})",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📅 Date de début", value=datetime.now().strftime("%d/%m/%Y à %H:%M"), inline=False)
        embed.set_footer(text=f"Démarrée par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        print(f"Erreur lors du démarrage de la saison : {e}")
        return await send_ephemeral_message(interaction, "❌ Erreur lors du démarrage de la nouvelle saison.")

@seasonCmd.command(name="terminer", description="Terminer la saison en cours")
async def end_season(interaction: discord.Interaction):
    """Termine la saison actuellement active."""
    if not is_admin(interaction):
        return await send_ephemeral_message(interaction, "❌ Seul un chef de guilde peut terminer la saison en cours.")

    # Vérifier qu'il y a une saison active
    current_season = get_active_season()
    if not current_season:
        return await send_ephemeral_message(interaction, "❌ Aucune saison n'est actuellement active.")

    try:
        # Terminer la saison
        success = end_current_season()
        if not success:
            return await send_ephemeral_message(interaction, "❌ Erreur lors de la terminaison de la saison.")
        
        embed = discord.Embed(
            title="🏁 Saison terminée !",
            description=f"**{current_season['name']}** (ID: {current_season['id']})",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        # Calculer la durée de la saison
        start_date = current_season['start_date']
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        duration = datetime.now() - start_date.replace(tzinfo=None)
        
        embed.add_field(name="📅 Démarrée le", value=start_date.strftime("%d/%m/%Y à %H:%M"), inline=True)
        embed.add_field(name="📅 Terminée le", value=datetime.now().strftime("%d/%m/%Y à %H:%M"), inline=True)
        embed.add_field(name="⏱️ Durée", value=f"{duration.days} jours", inline=False)
        embed.set_footer(text=f"Terminée par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        print(f"Erreur lors de la terminaison de la saison : {e}")
        return await send_ephemeral_message(interaction, "❌ Erreur lors de la terminaison de la saison.")

@seasonCmd.command(name="info", description="Afficher les informations sur la saison en cours")
async def season_info(interaction: discord.Interaction):
    """Affiche les informations sur la saison actuelle."""
    current_season = get_active_season()
    
    if not current_season:
        return await send_ephemeral_message(interaction, "❌ Aucune saison n'est actuellement active.")
    
    start_date = current_season['start_date']
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    
    # Calculer la durée depuis le début
    duration = datetime.now() - start_date.replace(tzinfo=None)
    
    embed = discord.Embed(
        title="📊 Saison en cours",
        description=f"**{current_season['name']}** (ID: {current_season['id']})",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    embed.add_field(name="📅 Démarrée le", value=start_date.strftime("%d/%m/%Y à %H:%M"), inline=True)
    embed.add_field(name="⏱️ Durée", value=f"{duration.days} jours", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@seasonCmd.command(name="historique", description="Afficher l'historique de toutes les saisons")
async def season_history(interaction: discord.Interaction):
    """Affiche l'historique de toutes les saisons."""
    seasons = get_all_seasons()
    
    if not seasons:
        return await send_ephemeral_message(interaction, "❌ Aucune saison n'a encore été créée.")
    
    embed = discord.Embed(
        title="📚 Historique des saisons",
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )
    
    for season in seasons[:10]:  # Limiter à 10 saisons pour éviter les embeds trop longs
        start_date = season['start_date']
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        status = "🟢 Active" if season['is_active'] else "🔴 Terminée"
        
        if season['end_date']:
            end_date = season['end_date']
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            duration = end_date.replace(tzinfo=None) - start_date.replace(tzinfo=None)
            duration_text = f"{duration.days} jours"
        else:
            duration = datetime.now() - start_date.replace(tzinfo=None)
            duration_text = f"{duration.days} jours (en cours)"
        
        embed.add_field(
            name=f"{season['name']} (ID: {season['id']})",
            value=f"{status}\n📅 {start_date.strftime('%d/%m/%Y')}\n⏱️ {duration_text}",
            inline=True
        )
    
    if len(seasons) > 10:
        embed.set_footer(text=f"... et {len(seasons) - 10} autres saisons")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

tree.add_command(seasonCmd)
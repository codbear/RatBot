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
    """
    Formate le classement avec un style plus attrayant
    """
    if not title:
        title = f"🏆 **CLASSEMENT DES RATS DU LARGE** 🏆\n🏴‍☠️ Saison: **{season}** 🏴‍☠️"

    lines = [title, ""]  # Ligne vide après le titre
    
    # Emojis pour les positions
    position_emojis = {
        1: "🏅",
        2: "🥇",  
        3: "🥈",
        4: "🥉",
    }
    
    # Afficher tous les pirates sans limitation
    previous_amount = None
    current_rank = 0
    display_rank = 0
    
    for idx, (uid, amount) in enumerate(ranking.items(), start=1):
        user = guild.get_member(uid)
        name = user.display_name if user else f"<@{uid}>"
        
        # Gestion des ex aequo : même score = même rang
        if amount != previous_amount:
            current_rank = idx
            display_rank = current_rank
        # Si même score que le précédent, on garde le même rang d'affichage
        
        # Emoji pour la position (basé sur le rang d'affichage)
        position_emoji = position_emojis.get(display_rank, "🏴‍☠️")
        
        # Formatage spécial pour les 4 premiers JOUEURS seulement (pas rangs)
        if idx <= 4:
            # Utiliser du texte en gras pour les 4 premiers joueurs
            lines.append(f"{position_emoji} **{display_rank}.** **{name}** • `{format_number(amount)} gold` 💰")
        else:
            # Style normal pour les autres positions
            lines.append(f"{position_emoji} **{display_rank}.** {name} • `{format_number(amount)} gold`")
        
        previous_amount = amount
    
    # Footer avec statistiques
    total_pirates = len(ranking)
    total_gold = sum(ranking.values())
    
    lines.append("")  # Ligne vide avant les stats
    lines.append("─" * 40)  # Ligne de séparation
    lines.append(f"📊 **{total_pirates}** pirates • **{format_number(total_gold)}** gold total")

    return "\n".join(lines)

async def update_ranking(interaction: discord.Interaction):
    # Vérifier qu'une saison est active
    active_season = get_active_season()
    if not active_season:
        # Si aucune saison active, ne pas faire d'erreur mais ne rien faire
        return
    
    season_name = active_season['name']
    ranking = calculate_ranking(season_name)
    
    # Utiliser le format texte amélioré
    message = format_ranking(interaction.guild, ranking, season_name)
    
    ranking_channel = interaction.guild.get_thread(int(os.getenv('RANKING_CHANNEL_ID'))) or interaction.guild.get_channel(int(os.getenv('RANKING_CHANNEL_ID')))

    if ranking_channel:
        # Chercher le message précédent du bot pour le mettre à jour
        async for msg in ranking_channel.history(limit=50):
            if msg.author == interaction.client.user:
                try:
                    await msg.edit(content=message)
                    return
                except discord.NotFound:
                    # Le message a été supprimé, en créer un nouveau
                    break
                except Exception:
                    # Autres erreurs, essayer d'envoyer un nouveau message
                    break
        
        # Si aucun message précédent trouvé, en envoyer un nouveau
        await ranking_channel.send(message)
    else:
        # Canal de classement non trouvé, envoyer dans le canal actuel
        await interaction.channel.send(message)
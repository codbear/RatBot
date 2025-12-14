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

def format_ranking(guild, ranking, season, title=None, exclude_user_id=None):
    """
    Formate le classement avec un style plus attrayant
    """
    if not title:
        title = f"# 🏆 CLASSEMENT DES RATS DU LARGE - {season} 🏆 #"

    lines = [title, ""]  # Ligne vide après le titre
    
    # Emojis pour les positions
    position_emojis = {
        1: "🥇",
        2: "🥈",
        3: "🥉",
        4: "🏅",
    }
    
    # Filtrer l'utilisateur exclu du classement si spécifié
    filtered_ranking = {}
    for uid, amount in ranking.items():
        if exclude_user_id is None or uid != exclude_user_id:
            filtered_ranking[uid] = amount
    
    # Afficher tous les pirates sans limitation (sauf celui exclu)
    previous_amount = None
    current_rank = 0
    display_rank = 0
    
    for idx, (uid, amount) in enumerate(filtered_ranking.items(), start=1):
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
    
    # Footer avec statistiques (utiliser le classement filtré)
    total_pirates = len(filtered_ranking)
    total_gold = sum(filtered_ranking.values())
    
    lines.append("")  # Ligne vide avant les stats
    lines.append("─" * 40)  # Ligne de séparation
    lines.append(f"📊 **{total_pirates}** pirates • **{format_number(total_gold)}** gold total")

    return "\n".join(lines)

def format_user_ranking_position(guild, ranking, season, user_id):
    """
    Affiche uniquement la position d'un utilisateur spécifique dans le classement
    """
    if not ranking:
        return f"❌ Aucune donnée pour la saison **{season}**"
    
    # Trouver la position de l'utilisateur
    user_position = None
    user_amount = None
    user_rank = None
    
    previous_amount = None
    current_rank = 0
    display_rank = 0
    
    for idx, (uid, amount) in enumerate(ranking.items(), start=1):
        # Gestion des ex aequo
        if amount != previous_amount:
            current_rank = idx
            display_rank = current_rank
            
        if uid == user_id:
            user_position = idx
            user_amount = amount
            user_rank = display_rank
            break
            
        previous_amount = amount
    
    if user_position is None:
        return f"😕 Tu n'es pas encore classé dans la saison **{season}**"
    
    user = guild.get_member(user_id)
    name = user.display_name if user else f"<@{user_id}>"
    
    # Emojis pour les positions
    position_emojis = {
        1: "🥇",
        2: "🥈", 
        3: "🥉",
        4: "🏅",
    }
    
    position_emoji = position_emojis.get(user_rank, "🏴‍☠️")
    
    # Message avec contexte
    total_players = len(ranking)
    
    result_lines = [
        f"🔍 **Ta position dans le classement :**",
        f"",
        f"{position_emoji} **{user_rank}.** **{name}** • `{format_number(user_amount)} gold` ⭐",
        f"",
        f"📊 Tu es **{user_rank}/{total_players}** dans la **{season}**"
    ]
    
    # Ajouter contexte si pas dans le top 4
    if user_rank > 4 and len(ranking) >= 4:
        # Montrer combien d'or il faut pour atteindre la 4ème place
        fourth_place_amount = list(ranking.values())[3]  # 4ème dans la liste (index 3)
        gold_needed = fourth_place_amount - user_amount + 1
        result_lines.append(f"🎯 Il te faut **{format_number(gold_needed)} gold** pour atteindre le top 4")
    
    return "\n".join(result_lines)

async def update_ranking(interaction: discord.Interaction, exclude_user_id=None):
    # Vérifier qu'une saison est active
    active_season = get_active_season()
    if not active_season:
        # Si aucune saison active, ne pas faire d'erreur mais ne rien faire
        return
    
    season_name = active_season['name']
    ranking = calculate_ranking(season_name)
    
    # Utiliser l'ID d'exclusion depuis l'environnement si non spécifié
    if exclude_user_id is None:
        exclude_from_env = os.getenv('EXCLUDE_FROM_RANKING')
        if exclude_from_env:
            try:
                exclude_user_id = int(exclude_from_env)
            except ValueError:
                pass  # Ignorer si pas un nombre valide
    
    # Utiliser le format texte amélioré avec exclusion optionnelle
    message = format_ranking(interaction.guild, ranking, season_name, exclude_user_id=exclude_user_id)
    
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
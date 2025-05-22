# commands/voyages.py
import os
import discord
from discord import app_commands
from core.bot import tree
from utils import format_number
from utils.check_role import is_admin
from utils.embed import post_voyage_embed
from utils.storage import voyages, save_data
from utils.ranking import update_ranking
from utils.send import send_ephemeral_message

def get_voyage_by_id(voyage_id: int):
    return next((v for v in voyages if v['id'] == voyage_id), None)

@app_commands.command(name="ajouter_voyage", description="Déclarer un voyage de guilde")
@app_commands.describe(
    gold="Montant d'or gagné pendant le voyage",
    membre1="Premier membre de l'équipage (facultatif)",
    membre2="Deuxième membre de l'équipage (facultatif)",
    membre3="Troisième membre de l'équipage (facultatif)"
)
async def add_voyage(
    interaction: discord.Interaction,
    gold: int,
    membre1: discord.Member = None,
    membre2: discord.Member = None,
    membre3: discord.Member = None
):
    season = interaction.channel.name
    # Déterminer le numéro du voyage
    season_voyages = [v for v in voyages if v.get('season') == season]
    crew_ids = [m.id for m in (membre1, membre2, membre3) if m]
    members_ids = [interaction.user.id] + crew_ids
    voyage_id = season_voyages[-1]['id'] + 1 if season_voyages else 1

    voyage = {
        'id': voyage_id,
        'gold': gold,
        'members': members_ids,
        'author': interaction.user.id,
        'timestamp': interaction.created_at.isoformat(),
        'season': interaction.channel.name
    }

    voyages.append(voyage)

    try:
        save_data()
        await post_voyage_embed(voyage, interaction)

        try:
            await update_ranking(interaction)
            return await send_ephemeral_message(interaction, f"✅ Voyage n°{voyage_id} enregistrée avec succès. Le classement a été mis à jour.")

        except Exception as e:
            print(f"Error updating ranking : {e}")
            return await send_ephemeral_message(interaction, "✅ Voyage n°{voyage_id} enregistrée avec succès. Cependant, une erreur est survenue lors de la mise à jour du classement. Tu peux demander à un chef de guilde de le mettre à jour manuellement.")

    except Exception as e:
        print(f"Error saving voyage : {e}")
        return await send_ephemeral_message(interaction, "❌ Une erreur est survenue lors de l'enregistrement du voyage.")

tree.add_command(add_voyage)
print("📌 Commande /add_voyage chargée depuis voyages.py")

# ----- COMMANDE: REMOVE VOYAGE -----
@app_commands.command(name="supprimer_voyage", description="Supprimer un voyage pour la saison en cours")
@app_commands.describe(index="Numéro du voyage à supprimer")
async def remove_voyage(interaction: discord.Interaction, index: int):
    if not is_admin(interaction):
        return await send_ephemeral_message(interaction, "❌ Seul un chef de guilde peut modifier un voyage.")
    
    voyage_to_remove = get_voyage_by_id(index)
        
    if not voyage_to_remove:
        return await send_ephemeral_message(interaction, f"❌ Le voyage n°{index} n'existe pas.")
    
    voyages.remove(voyage_to_remove)

    save_data()

    await send_ephemeral_message(interaction, f"🗑️ Voyage n°{index} supprimé.")

tree.add_command(remove_voyage)
print("📌 Commande /remove_voyage chargée depuis voyages.py")

# ----- COMMANDE: EDIT VOYAGE -----
@app_commands.command(name="modifier_voyage", description="Modifier le montant d'un voyage.")
@app_commands.describe(index="Numéro du voyage à modifier", gold="Nouveau montant d'or gagné")
async def edit_voyage(interaction: discord.Interaction, index: int, gold: int):
    if not is_admin(interaction):
        return await send_ephemeral_message(interaction, "❌ Seul un chef de guilde peut modifier un voyage.")
    
    voyage_to_edit = get_voyage_by_id(index)
    
    if not voyage_to_edit:
        return await send_ephemeral_message(interaction, f"❌ Le voyage n°{index} n'existe pas.")
    
    voyage_to_edit['gold'] = gold

    save_data()

    await send_ephemeral_message(interaction, f"✏️ Voyage n°{index} mis à jour à {format_number(gold)} pièces d'or.")

tree.add_command(edit_voyage)
print("📌 Commande /edit_voyage chargée depuis voyages.py")

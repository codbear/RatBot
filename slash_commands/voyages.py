# commands/voyages.py
import discord
from discord import app_commands
from core.bot import tree
from utils.format_number import format_number
from utils.check_role import is_admin
from utils.embed import post_voyage_embed
from utils.send import send_ephemeral_message
from utils.db import insert_voyage, delete_voyage, update_voyage
from utils.ranking import update_ranking

@app_commands.command(name="ajouter_voyage", description="Déclarer un voyage de guilde")
@app_commands.describe(
    gold="Montant d'or gagné pendant le voyage",
    emissaire="Valeur d'émissaire de guilde gagnée pendant le voyage",
    membre1="Premier membre de l'équipage (facultatif)",
    membre2="Deuxième membre de l'équipage (facultatif)",
    membre3="Troisième membre de l'équipage (facultatif)"
)
async def add_voyage(
    interaction: discord.Interaction,
    gold: int,
    emissaire: int,
    membre1: discord.Member = None,
    membre2: discord.Member = None,
    membre3: discord.Member = None
):
    season = interaction.channel.name
    members_ids = [interaction.user.id] + [m.id for m in (membre1, membre2, membre3) if m]

    voyage = {
        'gold': gold,
        'emissary_value': emissaire,
        'members': members_ids,
        'author': interaction.user.id,
        'timestamp': interaction.created_at.isoformat(),
        'season': season
    }

    # Enregistrement en DB
    try:
        new_id = insert_voyage(voyage)
        voyage['id'] = new_id
        await post_voyage_embed(voyage, interaction)
    except Exception as e:
        print(f"Error saving voyage: {e}")
        return await send_ephemeral_message(interaction, "❌ Erreur lors de l'enregistrement du voyage.")

    # Mise à jour du classement
    try:
        await update_ranking(interaction)
        return await send_ephemeral_message(
            interaction,
            f"✅ Voyage n°{new_id} enregistré et classement mis à jour."
        )
    except Exception as e:
        print(f"Error updating ranking : {e}")
        return await send_ephemeral_message(
            interaction,
            f"✅ Voyage n°{new_id} enregistré. Erreur lors de la mise à jour du classement."
        )

# Enregistrement de la commande
tree.add_command(add_voyage)
print("📌 Commande /add_voyage chargée depuis voyages.py")


@app_commands.command(name="supprimer_voyage", description="Supprimer un voyage par ID pour la saison en cours")
@app_commands.describe(voyage_id="ID du voyage à supprimer")
async def remove_voyage(interaction: discord.Interaction, voyage_id: int):
    if not is_admin(interaction):
        return await send_ephemeral_message(interaction, "❌ Seul un chef de guilde peut supprimer un voyage.")

    # Suppression en DB
    season = interaction.channel.name
    deleted = delete_voyage(season, voyage_id)
    if not deleted:
        return await send_ephemeral_message(
            interaction,
            f"❌ Le voyage n°{voyage_id} n'existe pas."
        )

    await send_ephemeral_message(
        interaction,
        f"🗑️ Voyage n°{voyage_id} supprimé."
    )
    # Mise à jour du classement
    await update_ranking(interaction)

# Enregistrement suppression
tree.add_command(remove_voyage)
print("📌 Commande /supprimer_voyage chargée depuis voyages.py")


@app_commands.command(name="modifier_voyage", description="Modifier le montant d'or d'un voyage.")
@app_commands.describe(
    voyage_id="ID du voyage à modifier",
    gold="Nouveau montant d'or gagné",
    emissaire="Nouvelle valeur d'émissaire de guilde gagnée"
)
async def edit_voyage(interaction: discord.Interaction, voyage_id: int, gold: int, emissaire: int):
    if not is_admin(interaction):
        return await send_ephemeral_message(interaction, "❌ Seul un chef de guilde peut modifier un voyage.")

    season = interaction.channel.name
    updated = update_voyage(season, voyage_id, gold, emissaire)
    if not updated:
        return await send_ephemeral_message(
            interaction,
            f"❌ Le voyage n°{voyage_id} n'existe pas."
        )

    await send_ephemeral_message(
        interaction,
        f"✏️ Voyage n°{voyage_id} mis à jour à {format_number(gold)} pièces d'or et {format_number(emissaire)} en valeur d'émissaire."
    )
    # Mise à jour du classement
    await update_ranking(interaction)

# Enregistrement modification
tree.add_command(edit_voyage)
print("📌 Commande /modifier_voyage chargée depuis voyages.py")

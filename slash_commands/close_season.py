# commands/archive.py
import discord
from core.bot import tree
from utils.storage import voyages, archives, save_data, save_archives
from utils.ranking import calculate_total_gold, format_ranking

@tree.command(name="close-season", description="Archiver la saison en cours et publier le classement définitif")
async def close_season(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("❌ Vous n'avez pas la permission d'archiver la saison.", ephemeral=True)
        return

    saison_name = interaction.channel.name
    gold_data = calculate_total_gold(saison_name)
    classement_message = format_ranking(interaction.guild, gold_data, saison_name)

    # Archivage
    archives[saison_name] = gold_data
    save_archives()

    # Suppression des sessions de cette saison
    voyages[:] = [s for s in voyages if s.get('saison') != saison_name]
    save_data()

    await interaction.response.send_message("📦 Saison archivée et classement final publié.", ephemeral=True)
    await interaction.channel.send(f"📦 Saison **{saison_name}** archivée ! Voici le classement final :\n" + classement_message)

print("📌 Commande /close-season chargée depuis close_season.py.")
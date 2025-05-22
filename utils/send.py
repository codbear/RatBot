import discord


async def send_ephemeral_message(interaction: discord.Interaction, message: str):
    """
    Envoie un message éphémère à l'utilisateur qui a déclenché l'interaction.
    """
    await interaction.response.send_message(message, ephemeral=True)
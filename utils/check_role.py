import discord


def is_admin(interaction: discord.Interaction):
    role = discord.utils.find(lambda r: r.name == 'Chef.fe de guilde', interaction.guild.roles)
    return role in interaction.user.roles
import discord
from discord.ext import commands

intents = discord.Intents.all
client = commands.Bot(command_prefix="!", intents=intents())

support_role = 'staff'
blacklisted_words = [
    "whore", 
    "slut"
    ]

bot_status = "Support Online"

token = ''
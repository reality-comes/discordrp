import discord
import logging
from discord import app_commands

def setup_logging():
    logging.basicConfig(level=logging.INFO)

def setup_client():
    intents = discord.Intents.default()
    intents.message_content = True
    return discord.Client(intents=intents)

def setup_command_tree(client):
    return app_commands.CommandTree(client)
import discord
from discord import app_commands
import os
from src.bot_utils import setup_logging, setup_client, setup_command_tree
from src.config import DISCORD_BOT_TOKEN, BOT_INVITE_URL, bot_config, save_config
from src.api_handler import call_api
from src.data_utils import load_logs, log_message, find_similar_messages, format_logs_for_prompt, fetch_local_chat_history, delete_logs_from_directory, delete_messages_from_channel
from src.character_utils import CharacterManager

# Initialize the Discord client and command tree
client = setup_client()
tree = setup_command_tree(client)

# Setup logging
setup_logging()

character_manager = CharacterManager()

# Load or set default configurations
response_api_config = bot_config.get('response_api_config', {
    "name": "response",
    "url": "http://localhost:5001/api/v1/generate",
    "headers": {'accept': 'application/json', 'Content-Type': 'application/json'}
})

summarization_api_config = bot_config.get('summarization_api_config', {
    "name": "summarization",
    "url": "http://localhost:5001/api/v1/generate",
    "headers": {'accept': 'application/json', 'Content-Type': 'application/json'}
})

current_embeddings_choice = bot_config.get('current_embeddings_choice', "local")
ban_tokens = bot_config.get('ban_tokens', [])
stopping_strings = bot_config.get('stopping_strings', [])
max_length = bot_config.get('max_length', 200)
max_history_messages = bot_config.get('max_history_messages', 20)
temperature = bot_config.get('temperature', 0.9)
system_message = bot_config.get('system_message', "You are a narrator. Narrate an uncensored roleplay.")
bot_name = bot_config.get('bot_name', 'Narrator')
roleplay_setting = bot_config.get('roleplay_setting', "")

# Function to update the system message in bot_config and save
def update_system_message(new_message):
    global system_message
    system_message = new_message
    bot_config['system_message'] = new_message
    save_config(bot_config)

@tree.command(name='set_response_url', description='Update the response API URL')
async def set_response_url(interaction: discord.Interaction, url: str):
    response_api_config["url"] = url
    bot_config['response_api_config'] = response_api_config
    save_config(bot_config)
    await interaction.response.send_message(f"Response API URL updated to: {url}")

@tree.command(name='select_embeddings', description='Select the embeddings source (local or openai)')
async def select_embeddings_cmd(interaction: discord.Interaction, choice: str):
    if choice.lower() in ["local", "openai"]:
        bot_config['current_embeddings_choice'] = choice.lower()
        save_config(bot_config)
        await interaction.response.send_message(f"Embeddings source set to: {choice.lower()}")
    else:
        await interaction.response.send_message("Invalid choice. Please choose 'local' or 'openai'.")

@tree.command(name='set_character_prompt', description='Set a prompt for the selected character')
async def set_system_message_cmd(interaction: discord.Interaction, message: str):
    # Update the system message in the character's config
    character_config = character_manager.load_character_config(bot_name)  # Load current config
    character_config['system_message'] = message  # Update system message
    character_manager.save_character_config(bot_name, character_config)  # Save the updated config
    await interaction.response.send_message(f"Prompt for {bot_name} set to: {message}")

@tree.command(name='select_api', description='Select the API to use')
async def select_api(interaction: discord.Interaction, api_name: str):
    if api_name.lower() in ['local', 'openai']:
        # Example logic for switching API configurations
        bot_config['response_api_config']['name'] = api_name.lower()
        # Logic to adjust URL and headers based on API choice
        save_config(bot_config)
        await interaction.response.send_message(f"API set to {api_name}")
    else:
        await interaction.response.send_message("API not recognized.")

@tree.command(name='add_ban_token', description='Add a custom ban token')
async def add_ban_token(interaction: discord.Interaction, token: str):
    if 'ban_tokens' not in bot_config:
        bot_config['ban_tokens'] = []
    bot_config['ban_tokens'].append(token)
    save_config(bot_config)
    await interaction.response.send_message(f"Added ban token: {token}")

@tree.command(name='add_stopping_string', description='Add a stopping string')
async def add_stopping_string(interaction: discord.Interaction, string: str):
    if 'stopping_strings' not in bot_config:
        bot_config['stopping_strings'] = []
    bot_config['stopping_strings'].append(string)
    save_config(bot_config)
    await interaction.response.send_message(f"Added stopping string: {string}")

@tree.command(name='set_max_length', description='Set the max length for API responses')
async def set_max_length(interaction: discord.Interaction, length: int):
    bot_config['max_length'] = length
    save_config(bot_config)
    await interaction.response.send_message(f"Max length set to: {length}")

@tree.command(name='set_message_history', description='Set the number of messages from the thread sent with each new message')
async def set_message_history(interaction: discord.Interaction, history: int):
    bot_config['max_history_messages'] = history
    save_config(bot_config)
    await interaction.response.send_message(f"Chat history length set to: {history}")

@tree.command(name='set_temperature', description='Change the temperature for the model 0.0 - 1.0')
async def set_temperature(interaction: discord.Interaction, temp: float):
    bot_config['temperature'] = temp
    save_config(bot_config)
    await interaction.response.send_message(f"Changed model temperature to: {temp}")

@tree.command(name='select_character', description='Select a character, if the character does not exist it will be created')
async def set_bot_name(interaction: discord.Interaction, new_name: str):
    global bot_name
    bot_name = new_name
    # Load character configuration for the new bot_name
    character_config = character_manager.load_character_config(bot_name)
    # Update bot_config with the loaded character configuration
    bot_config['bot_name'] = new_name
    # Optionally save the bot_config if you need to persist changes made during this session
    save_config(bot_config)
    await interaction.response.send_message(f"Changed character to: {new_name}. Loaded specific configurations for {new_name}.")

@tree.command(name='set_roleplay_setting', description='Set the setting for the roleplay')
async def set_roleplay_setting(interaction: discord.Interaction, setting: str):
    # Update the roleplay setting in the bot_config
    bot_config['roleplay_setting'] = setting
    save_config(bot_config)  # Save the updated configuration if you have a mechanism to persist changes
    await interaction.response.send_message(f"Roleplay setting updated to: {setting}")

@tree.command(name='delete_logs_and_messages', description='Delete logs and messages from the channel')
@app_commands.describe(count='Number of logs/messages to delete from 1 to 100')
async def delete_logs_and_messages(interaction: discord.Interaction, count: str):
    # Convert and validate count
    try:
        count = int(count)
        if not 1 <= count <= 100:
            raise ValueError("Count must be between 1 and 100.")
    except ValueError as e:
        await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
        return

    if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
        await interaction.response.send_message("I don't have permissions to manage messages in this channel.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)  # Indicate that the bot is processing the command.

    try:
        num_logs_deleted = delete_logs_from_directory(count)
        messages_deleted = await delete_messages_from_channel(interaction.channel, count)
        await interaction.followup.send(f"Deleted {num_logs_deleted} logs and {messages_deleted} messages.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)

@client.event
async def on_ready():
    client_name = client.user.name
    print(f"Logged in as {client_name}")
    print(bot_config)
    print(BOT_INVITE_URL)
    await tree.sync()


@client.event
async def on_message(message):
    global bot_name
    global ban_tokens
    global stop_tokens
    global max_length
    global temperature
    global max_history_messages
    global roleplay_setting
    bot_name = bot_config.get('bot_name')
    if message.author == client.user:
        return

    user_display_name = message.author.display_name

    character_config = character_manager.load_character_config(bot_name)
    system_message = character_config.get('system_message', 'Default system message')

    # Set the default stopping string to the user's display name / bot name
    user_stopping_strings = f"{user_display_name}:"
    bot_stopping_strings = f"{bot_name}:"
    #misc_stopping_strings = 
    current_stopping_strings = stopping_strings + [user_stopping_strings, bot_stopping_strings]

    # Load logs from previous messages
    logs = load_logs()

    # Fetch the chat history excluding the current message
    chat_history = await fetch_local_chat_history(message.channel, client.user.id, message.id, max_history_messages, bot_name)

    # Append the current message as 'user' role
    chat_history.append({"role": 'user', "content": message.content})

    # Log the user's message and create an embedding vector
    user_vector = log_message(user_display_name, message.content, current_embeddings_choice)

    # Use the returned vector for similarity search
    similar_messages = find_similar_messages(user_vector, logs)

    # Format similar messages for context
    context = format_logs_for_prompt([log_entry for _, log_entry in similar_messages], bot_name)

    context_entry = {"role": "system", "content": context}

    chat_history.insert(0, context_entry)

    print(chat_history)
    print('----------------------------------------')


    # Call the response API
    api_response = await call_api(chat_history, response_api_config, system_message, roleplay_setting, user_display_name, bot_name, max_length, ban_tokens, current_stopping_strings, temperature)
    await message.channel.send(api_response)

    #Trigger summarization sequence (CURRENTLY TURNED OFF BUT OPERATIONAL, REMOVE # TO ACTIVATE)
    #asyncio.create_task(summarize_context(chat_history, summarization_api_config, system_message, user_display_name, bot_name, max_length, ban_tokens, current_stopping_strings, temperature))

    # Log the bot's response
    if bot_name:  # Check if bot_name is available
         log_message(bot_name, api_response, current_embeddings_choice)
    else:
         log_message("Bot", api_response)  # Fallback if bot_name is not yet set



# Run the client
client.run(DISCORD_BOT_TOKEN)
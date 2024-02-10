import os
import json
import discord
from datetime import datetime
from src.embeddings import generate_embedding
from src.api_handler import call_api
from scipy import spatial


def log_message(sender, content, embeddings_source):
    global bot_name
    # Use the bot's name if it's the bot sending the message
    sender_name = bot_name if sender == "bot" and bot_name is not None else sender

    # Pass the embeddings source to generate_embedding
    vector = generate_embedding(content, embeddings_source)
    

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_data = {
        "timestamp": timestamp,
        "sender": sender_name,
        "content": content,
        "vector": vector
    }

    # Update the directory path
    log_directory = os.path.join('src', 'logs')
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    file_name = os.path.join(log_directory, f"message_{timestamp}.json")
    with open(file_name, 'w') as file:
        json.dump(log_data, file, indent=4)

    return vector


def load_json(file_path):
    # Assuming you have a function to load JSON data
    with open(file_path, 'r') as file:
        return json.load(file)

def load_logs():
    files = os.listdir('./src/logs')
    files = [i for i in files if '.json' in i]
    result = []
    for file in files:
        data = load_json('./src/logs/%s' % file)
        if data:
            result.append(data)
    ordered = sorted(result, key=lambda d: d['timestamp'], reverse=False)
    return ordered

def find_similar_messages(target_vector, all_logs, top_k=5):
    similarities = []
    for log_entry in all_logs:
        # Ensure 'vector' is present in log_entry
        if 'vector' in log_entry:
            similarity = 1 - spatial.distance.cosine(target_vector, log_entry['vector'])
            similarities.append((similarity, log_entry))

    # Sort by similarity in descending order
    similarities.sort(key=lambda x: x[0], reverse=True)

    # Return the top k most similar messages
    return similarities[:top_k]

def format_logs_for_prompt(similar_logs, bot_name):
    formatted_context = ""
    for log in similar_logs:
        role = "assistant" if log['sender'] == bot_name else "user"
        formatted_context += f"[{role}] you remember {log['sender']} saying: {log['content']}\n"
    return formatted_context

async def summarize_context(chat_history, api_config, system_message, user_name, bot_name, max_length, ban_tokens, stopping_strings, temperature):
    # Call the API with the summarization flag set to True
    summarized_context = await call_api(chat_history, api_config, system_message, user_name, bot_name, max_length, ban_tokens, stopping_strings, temperature, for_summarization=True)


async def fetch_local_chat_history(channel_id, bot_id, current_message_id, max_history_messages, bot_name):
    # Load the logs from local storage
    all_logs = load_logs()
    
    history = []
    for log_entry in all_logs[-max_history_messages:]:
        # Here, you might need a way to match logs to a specific channel if your logging includes messages from multiple channels
        # This example assumes all messages are relevant, but you could include a channel ID in your log entries to filter by channel

        # Skip the current message if logged
        if str(log_entry.get("message_id")) == str(current_message_id):
            continue

        role = "assistant" if log_entry["sender"] == bot_name else "user"  # Use the global bot_name or adjust as needed
        history_entry = {
            "role": role,
            "content": log_entry["content"]
            # You might also include other relevant details from your logs here
        }
        history.append(history_entry)

    # Assuming your logs are already in chronological order, but reverse if needed
    # history.reverse()
    return history

    return summarized_context

def delete_logs_from_directory(count):
    log_directory = os.path.join('src', 'logs')
    if not os.path.exists(log_directory):
        raise FileNotFoundError("Log directory does not exist.")
    files = sorted([os.path.join(log_directory, f) for f in os.listdir(log_directory) if f.endswith('.json')], key=os.path.getmtime)
    files_to_delete = files[-count:]

    for f in files_to_delete:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Error deleting log file {f}: {e}")  # Consider logging this properly
    
    return len(files_to_delete)

async def delete_messages_from_channel(channel, count):
    if count > 100:
        count = 100  # Enforce Discord's maximum limit to avoid errors
    
    try:
        deleted_messages = await channel.purge(limit=count, check=lambda msg: (discord.utils.utcnow() - msg.created_at).days < 14)
        return len(deleted_messages)
    except discord.Forbidden:
        raise Exception("Bot lacks permissions to delete messages.")
    except discord.HTTPException as e:
        raise Exception(f"Failed to delete messages: {e}")

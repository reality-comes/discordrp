import requests
import aiohttp
import openai
import os
import json

def format_local_prompt(chat_history, system_message, roleplay_setting, user_name, bot_name):
    if roleplay_setting:
        formatted_prompt = f"{system_message}\n\nSetting: {roleplay_setting}\n\n"
    else:
        formatted_prompt = system_message + '\n'
    
    for msg in chat_history:
        role = bot_name if msg['role'] == 'assistant' else user_name
        formatted_prompt += f'{role}:\n{msg["content"]}\n'
    formatted_prompt += f'{bot_name}:\n'  # Ensure it ends with the bot's name
    return formatted_prompt


async def call_api(chat_history, api_config, system_message, roleplay_setting, user_name, bot_name, max_length, ban_tokens, stopping_strings, temperature, for_summarization=False):
    prompt = ""
    if for_summarization:
        # Format the prompt for summarization
        prompt = "Summarize the following text:\n"
        prompt += "\n".join([f"{msg['content']}" for msg in chat_history])
    else:
        # Format the prompt for regular response generation (specific to your bot's design)
        prompt = format_local_prompt(chat_history, system_message, roleplay_setting, user_name, bot_name)

    if api_config["name"] == "openai":
        openai.api_key = os.environ.get("OPENAI_API_KEY")

        # Adjust the API call based on summarization or regular response
        if for_summarization:
            # Send summarization prompt to OpenAI
            response = openai.Completion.create(
                engine="gpt-3.5-turbo",
                prompt=prompt,
                max_tokens=max_length,
                temperature=temperature
            )
        else:
            # Send chat history for response generation
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=chat_history
            )

        # Debug print for OpenAI API call
        print("Sending to OpenAI:", json.dumps(chat_history if not for_summarization else prompt, indent=2))
        return response.choices[0].message.content if response.choices else "No response."

    elif api_config["name"] == "local" or api_config["name"] == "summarization":
        # Response API call handling using the formatted prompt
        url = api_config["url"]
        headers = api_config["headers"]

        data = {
            "prompt": prompt,
            "max_length": max_length,
            "custom_token_bans": ", ".join(ban_tokens),
            "stop_sequence": stopping_strings,
            "sampler_order": [6, 0, 1, 2, 3, 4, 5],
            "temperature": temperature,
            "trim_stop" : True
        }

        # Debugging: print data sent to response API
        print("Sending to Response API:", data)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status != 200:
                # Handle non-200 responses
                 raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status, message=response.reason, headers=response.headers)

                response_json = await response.json()

                # Debugging: print the raw response from response API
                print("Received from response API:", response_json)

                results = response_json.get("results")
                if results and len(results) > 0:
                    generated_text = results[0].get("text")
                    return generated_text if generated_text else "No response."
                else:
                    return "No response."

    else:
        raise ValueError("Invalid API selection")

    return "Error in processing the request"
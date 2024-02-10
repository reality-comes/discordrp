DiscordRP

This Discord bot is designed to offer dynamic interactions with locally hosted LLMs inside of a Discord server, featuring character roleplay, retrieval augmented generation (RAG), and custom API interactions for generating responses. It's built with Python and utilizes discord.py, the original intent of this bot was to rewrite my original bot, GPT-4-Discord-Bot-Long-Term-Memory, to work with locally hosted LLMs. In the process of doing so, I found it easier to start from scratch and added a significant number of features along the way.


Local LLM Support:

DiscordRP is designed around using locally hosted LLMs, as such I recommend using koboldcpp for easy setup, however, the bot should work with any LLM API, local or not, that utilizes the same framework. 


OpenAI Support:

Currently the bot does work with OpenAI LLMs and 3.5 Turbo is hardcoded, you can switch to OpenAI utilizing "/select_api openai" inside your chat channel. Changing from 3.5 is easy, but will require editing the code. Functionally, there is a loss using OpenAI LLMs and I don't recommend it.


Retrieval Augmented Generation (RAG):

RAG is how the bot extends its memory beyond the context allowed by the LLM (or your hardware). Each message is logged with a vector embedding and the bot retrieves relevant memories to add to the prompt for each message sent. It's certainly not perfect but it does help the bot remember details.


Embeddings:

RAG is done via vector embeddings, currently the bot uses OpenAI embeddings model ada-002 which does require an API key from OpenAI and its extremely cheap (pennies), optionally, "/select_embeddings local" can switch you to hardcoded local embeddings utilizing Swiss Army Llama on Docker. I have done very little work to make this better as my hardware doesn't really support running both locally. 


Characters:

Characters are managed via "/set_bot_name", setting a new name will generate a new character card, which simply contains prompt information for that character. The bot should default to "Narrator", which I personally find the best sort of base character for RP. 
To change the prompt for the character utilize "/set_system_message".


Setup:

1. Create a new Discord application
2. Turn ON Message content intent
3. Input token/client/server information in example.env *Token/client ID come from Discord application, Server ID comes from the Discord client (right-click on the server icon and it should be at the bottom of the popup menu)
4. Rename example.env to be .env
5. Create an OpenAI account and generate an API Key
6. Input OpenAI Key into .env
7. In Python install dependencies in requirements.txt
8. Run main.py
9. Open URL provided in terminal window to invite the bot to your Discord Server
10. Download KoboldCPP
11. Download GGUF model for KoboldCPP
12. Run and configure KoboldCPP
13. Start chatting

Bot Commands:

/set_system_message - Sets the primary portion of the prompt, this tells the LLM what you want it to do, this is where you input the character information and how the character should behave

/set_bot_name - Sets the name the bot will use for the next message, if its a new name you should /set_system_message to provide details for the new character

/set_roleplay_setting - This is optional, provides a fixed (or changing) setting information for the RP. Very important if you're switching characters often to maintain the setting details (when and where)

/delete_logs_and_messages - This deletes the input number of logs and messages from the server, important if you want to rewind the conversation or get a bad generation. 

/set_max_length - Sets the length of the response for the LLM, defaults to 200.

/set_message_history - Sets the number of past messages to include in the prompt, defaults to 20. The higher the better,but consider your hardware and the context length of the LLM and how long you want to wait for a response.

/set_temperature - Sets the temperature for the LLM, defaults to .9

/add_stopping_string - Adds stopping strings that will stop the LLM generation. Use this if the LLM is responding in ways you don't want, usually things like [user] will crop up from time to time, I probably can fix most of this later.

/select_api - "openai" OR "local", discussed above.

/set_response_url - Use this if you need to change where the API is listening, for instance if you're using cloudflare or LAN or change the KoboldCPP port.








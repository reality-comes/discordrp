import openai
import requests
import os


def generate_embedding(text, source="openai"):
    if source == "openai":
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text
        )
        # Return the embedding directly from OpenAI's response
        return response['data'][0]['embedding']

    elif source == "local":
        url = "http://localhost:8089/get_embedding_vector_for_string/"
        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
        data = {"text": text, "llm_model_name": "openchat_v3.2_super"}
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            # Convert response to JSON
            response_json = response.json()
            # Extract the embedding from local API response
            return response_json['embedding']
        else:
            raise Exception(f"Local API request failed with status code {response.status_code}")

    else:
        raise ValueError("Invalid embedding source specified")
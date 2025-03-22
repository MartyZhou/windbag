import os
import requests
from dotenv import load_dotenv

class CustomLlamaModel:
    def __init__(self, api_url, api_key):
        load_dotenv()
        self.api_url = api_url
        self.api_key = api_key

    def __call__(self, prompt):
        if hasattr(prompt, "to_string"):
            prompt = prompt.to_string()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": os.getenv("MODEL_NAME"),
            "prompt": prompt,
            "temperature": 0.7,
            "max_tokens": 10240
        }
        response = requests.post(self.api_url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise Exception(f"Error from AI Gateway: {response.status_code} - {response.text}")
# Importing necessary libraries
import json

import openai
import toml
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def __init__(self, config_path: str = ""):
        # System prompts
        self.system: str = ""
        self.instructions: str = ""
        self.latest: dict = {}

        self.concerned: bool = False
        self.templates: dict = {}

        self.knowledge: list = []
        self.messages: list = []

        if config_path:
            self.load_config(config_path)

    def load_config(self, path):
        # Loading the agent from the config file
        with open(path) as f:
            agent = toml.load(f)

        # Extracting core and instructions from the agent
        self.system = agent["system"]
        self.instructions = agent["instructions"]
        self.request = agent["request"]

        # Extracting templates
        self.templates["knowledge"] = agent["knowledge"]

    def think(self, statement):
        self.messages.append({"role": "user", "content": statement})
        self.messages = self.messages[-6:]

        messages_start = [
            {"role": "user", "content": self.system},
            {
                "role": "user",
                "content": "Here is our most recent conversation: \n",
            },
        ]

        messages_end = [
            # {"role": "user", "content": self.instructions},
            {"role": "user", "content": self.request},
        ]

        messages = messages_start + self.messages + messages_end

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        
        self.messages.append(
            {
                "role": "assistant",
                "content": json.loads(response.choices[0]  # type: ignore
                                      .message.content.strip())['response'],
            }
        )
        self.latest = json.loads(response.choices[0]  # type: ignore
                                .message.content.strip())
        return response
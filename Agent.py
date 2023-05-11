# Importing necessary libraries
import json

import openai
import toml


class Agent:
    def __init__(self, config_path: str = "", api_key: str = ""):
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
        self.templates["knowledge"] = "" #agent["knowledge"]

    def think(self, statement):
        if statement:
            self.messages.append({"role": "user", "content": statement})
        self.messages = self.messages[-6:]

        if self.knowledge:
            knowledge_message = "\n".join(f"- {k}" for k in self.knowledge)
            knowledge_message = (
                "Here is a list of things you know about me:\n" + knowledge_message
            )
        else:
            knowledge_message = "You don't know anything about me yet."

        messages = [{"role": "user", "content": self.system}]
        messages.append(
            {"role": "user", "content": "\n---\n<Latest Conversation>\nHere is our most recent conversation:\n"}
        )

        for m in self.messages:
            u = 'Me' if m['role']=='user' else 'You'
            content = f"{u}: {m['content']}"
            messages.append({"role": "user", "content": content})

        messages.append({"role": "user", "content": "\n---\n<Knowledge>\n"})
        messages.append({"role": "user", "content": knowledge_message})
        messages.append({"role": "user", "content": self.instructions})
        messages.append({"role": "user", "content": self.request})

        # print("\n".join([m["content"] for m in messages]))

        _response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        print(_response.choices[0].message.content.strip()) # type: ignore
        response = json.loads(
            _response.choices[0].message.content.strip()  # type: ignore
        )

        self.messages.append(
            {
                "role": "assistant",
                "content": response["response"],
            }
        )
        self.latest = response
        return response

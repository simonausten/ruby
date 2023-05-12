# Importing necessary libraries

import openai
from termcolor import colored
import toml


class Agent:
    def __init__(self, config_path, api_key: str = ""):
        self.conversation = ["You: Hi, I'm Ruby."]
        self.knowledge = []
        self.autobiography = "I am a British child between 5 and 18 years old."
        self.concern = False
        self.load_config(config_path)

    def load_config(self, path):
        # Loading the agent from the config file
        with open(path) as f:
            agent = toml.load(f)

        # Extracting core and instructions from the agent
        self.prompt_template = agent["prompt_template"]

    def parse_response(self, r):
        # TODO: Error handling. Lots of error handling.
        r = r.choices[0].message.content.strip()  # type: ignore
        print(colored(r, 'green'))
        response_key, response, autobiography_key, autobiography, concern_key, concern = [
            _.strip() for _ in r.split("|")[1:]
        ]
        return {
            response_key: response.replace('"', "")
            .replace("\n", "")
            .strip(),
            autobiography_key: autobiography.replace('"', "")
            .replace("\n", "")
            .strip(),
            concern_key: True if "TRUE" in concern.upper() else False,
        }

    def think(self, statement):
        # Prepare
        self.conversation.append(f"Me: {statement}")
        # TODO: Truncate conversation
        # self.conversation = self.conversation[-6:]
        conversation = "\n".join(self.conversation)
        print(colored(conversation, 'light_blue'))

        # if self.knowledge:
        #     knowledge = "\n".join(f"- {k}" for k in self.knowledge)
        # else:
        #     knowledge = ""

        prompt = self.prompt_template.format(
            conversation=conversation, autobiography=self.autobiography
        )

        # Call
        # TODO: Catch RateLimitError
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        response = self.parse_response(response)

        print(colored(str(response), 'blue'))

        # Update
        self.conversation.append(f"You: {response['response']}")
        # self.knowledge = [
        #     _
        #     for _ in response["knowledge"]
        #     if len(_) > 2 and not _.lower().startswith("nothing")
        # ]
        self.autobiography = response['autobiography']
        self.concern = response['concern']

        return response

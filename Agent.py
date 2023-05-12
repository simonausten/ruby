# Importing necessary libraries

import time
import openai
from termcolor import colored
import toml


class Agent:
    def __init__(self, config_path, api_key: str = ""):
        self.knowledge = []
        self.autobiography = "I am a British child between 5 and 18 years old."
        self.concern = False
        self.load_config(config_path)

    def load_config(self, path):
        # Loading the agent from the config file
        with open(path) as f:
            agent = toml.load(f)

        self.gambit = agent["gambit"]
        self.prompt_template = agent["prompt_template"]

    def parse_response(self, r):
        # TODO: Error handling. Lots of error handling.
        r = r.choices[0].message.content.strip()  # type: ignore
        print(colored(r, "green"))
        # TODO: Handle ValueError (not enough values to unpack)
        (
            response_key,
            response,
            autobiography_key,
            autobiography,
            concern_key,
            concern,
        ) = [_.strip() for _ in r.split("|")[1:]]
        return {
            response_key: response.replace('"', "").replace("\n", "").strip(),
            autobiography_key: autobiography.replace('"', "").replace("\n", "").strip(),
            concern_key: True if "TRUE" in concern.upper() else False,
        }

    def think(self, history):
        # Prepare
        conversation = []
        for statement in history:
            name = "Me" if statement["role"] == "user" else "You"
            conversation.append(f"{name}: {statement['content']}")

        # TODO: Truncate conversation

        conversation = "\n".join(conversation)
        print(colored(conversation, "light_blue"))

        prompt = self.prompt_template.format(
            conversation=conversation, autobiography=self.autobiography
        )

        # Call
        response = None
        # TODO: Catch RateLimitError
        for i in range(3):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )
                break
            except:
                print(colored("OpenAI API is slow, retrying...", "yellow"))
                time.sleep(3)

        # TODO: Catch empty response
        response = self.parse_response(response)

        print(colored(str(response), "blue"))

        # Update
        self.autobiography = response["autobiography"]
        self.concern = response["concern"]

        return response

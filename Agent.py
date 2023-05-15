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

    def get_default_response(self):
        (response_key, response) = (
            "response",
            "Sorry, I'm having a technical issue. Please can you say that again?",
        )
        (autobiography_key, autobiography) = ("autobiography", self.autobiography)
        (concern_key, concern) = ("concern", self.concern)

        return {
            response_key: response,
            autobiography_key: autobiography,
            concern_key: concern,
        }

    def sanitise_response(self, r: str) -> dict:
        ########################################
        # String Sanitisation
        ########################################

        # Handle quoted delimiters
        r = "\n".join([_.strip('"') for _ in r.split("\n")])

        # Handle missing "response"
        if not r.startswith("|response|"):
            r = "|response|\n" + r

        ########################################
        # Array Sanitisation
        ########################################

        r_split = [_.strip() for _ in r.split("|")[1:]]

        if len(r_split) != 6:
            r_dict = self.get_default_response()
        else:
            (
                response_key,
                response,
                autobiography_key,
                autobiography,
                concern_key,
                concern,
            ) = r_split
            r_dict = {
                response_key: response.replace('"', "").replace("\n", "").strip(),
                autobiography_key: autobiography.replace('"', "")
                .replace("\n", "")
                .strip(),
                concern_key: True if "TRUE" in concern.upper() else self.concern,
            }

        return r_dict

    def parse_response(self, r):
        # TODO: Error handling. Lots of error handling.
        r = r.choices[0].message.content.strip()  # type: ignore
        print(colored(r, "green"))

        r_dict = self.sanitise_response(r)
        return r_dict

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
            except Exception as api_error:  # openai.APIError as api_error:
                print(colored(repr(api_error), "yellow"))
                print(colored("OpenAI API is slow, retrying...", "yellow"))
                time.sleep(3)

        # TODO: Catch empty response
        response = self.parse_response(response)

        print(colored(str(response), "blue"))

        # Update
        self.autobiography = response["autobiography"]
        self.concern = response["concern"]

        return response

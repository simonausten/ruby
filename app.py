# Importing necessary libraries
from datetime import datetime
import os
import toml
import openai

# Setting the environment variable for OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = "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"

# llm = OpenAI()  # type: ignore

def log(s):
    print(s)
    with open("therapist.md", 'a') as log:
        log.write("# " + str(s) + "\n")

log("---\n# NEW SESSION: {}\n".format(datetime.now().strftime("%B %d, %Y %H:%M:%S")))

class Agent:
    def __init__(self, config_path: str = ""):
        # System prompts
        self.core: str = ""
        self.instructions: str = ""

        self.concerned: bool = False
        self.templates: dict = {}

        self.statement: str = ""
        self.knowledge: list = []
        self.history: list = []

        if config_path:
            self.load_config(config_path)

    def load_config(self, path):
        # Loading the agent from the config file
        with open(path) as f:
            agent = toml.load(f)

        # Extracting core and instructions from the agent
        self.core = agent["system"]
        self.instructions = agent["instructions"]
        self.output = agent["output"]

        # Extracting templates
        self.templates["knowledge"] = agent["knowledge"]
        self.templates["latest_statement"] = agent["latest_statement"]
        self.templates["history"] = agent["history"]

    def format_statement(self) -> str:
        return self.templates['latest_statement'].format(latest_statement=self.statement)

    def format_knowledge(self) -> str:
        return self.templates["knowledge"].format(
            knowledge="\n".join([f"- {i}" for i in self.knowledge])
        )

    def format_history(self) -> str:
        return self.templates["history"].format(
            history="\n".join(
                [f"- {agent}: {statement}" for (agent, statement) in self.history]
            )
        )

    def get_prompt(self) -> str:
        prompt = "\n\n".join(
            [
                self.core,
                self.format_knowledge(),
                self.format_history(),
                self.format_statement(),
                self.instructions,
                self.output
            ]
        )

        return prompt

    def think(self, statement):
        self.statement = statement

        prompt = self.get_prompt()

        os.system('cls' if os.name == 'nt' else 'clear')
        log(prompt)

        """ Call LLM """
        # response = llm(prompt)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": prompt}]
        )
        log(response)

        """ Comment? """
        log("---\n# Notes: {}".format(input(">>> Bugs or comments?: ")))

        """ Process response """

        # response = json.loads(response)  # TODO: Error checking

        # self.knowledge = response["knowledge"]
        # self.history.append(["Child", statement])
        # self.history.append(["Therapist", response["response"]])

        # # 3. If necessary, truncate the history
        # self.history = self.history[-4:]

        return response


therapist = Agent(config_path="./agents/therapist.toml")
message = "Hi"

while True:
    therapist.load_config('./agents/therapist.toml')
    message = "Hi"
    response = therapist.think(message)
    print(response.choices[0].message.content)
    message = input("> ")

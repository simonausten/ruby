# Importing necessary libraries
from datetime import datetime
import json
import os
from typing import Tuple
import gradio as gr
import toml
from langchain.llms import OpenAI

# Setting the environment variable for OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"

llm = OpenAI()  # type: ignore

def log(s):
    print(s)
    with open("therapist.md", 'a') as log:
        log.write("# " + s + "\n")

log("---\n# NEW SESSION: {}\n".format(datetime.now().strftime("%B %d, %Y %H:%M:%S")))

class Agent:
    def __init__(self, config_path: str = ""):
        # System prompts
        self.core: str = ""
        self.reflection: str = ""
        self.instructions: str = ""

        self.concerned: bool = False
        self.templates: dict = {}

        self.statement: str = ""
        self.knowledge: list = []
        self.history: list = [
            ["Therapist", "(You are waiting calmly for your patient. You have never met them before.)"]
        ]  # noqa: E501

        if config_path:
            self.load_config(config_path)

    def load_config(self, path):
        # Loading the agent from the config file
        with open(path) as f:
            agent = toml.load(f)

        # Extracting core, reflection and instructions from the agent
        self.core = agent["system"]
        self.reflection = agent["reflection"]
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
            important="\n".join([f"- {i}" for i in self.knowledge])
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
                self.reflection,
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
        response = llm(prompt)
        log(response)

        """ Comment? """
        log("---\n# Notes: {}".format(input(">>> Bugs or comments?: ")))

        """ Process response """

        response = json.loads(response.strip())  # TODO: Error checking

        self.knowledge = response["knowledge"]
        self.history.append(["Child", statement])
        self.history.append(["Therapist", response["response"]])

        # 3. If necessary, truncate the history
        self.history = self.history[-4:]

        return response


therapist = Agent(config_path="./agents/therapist.toml")


def process(
     message: str, chat_history: list
) -> Tuple[str, list, list]:
    global therapist #TODO: bad smell
    therapist.think(message)

    return ("", therapist.history, therapist.knowledge)


with gr.Blocks(
    theme=gr.themes.Soft(),
    css="""
        #memory {font-size: 10px; font-style: italic;}
        #warning {background: red; color: white; filter: filter: grayscale(0%) !important;}
        button[disabled] {filter: grayscale(0%) !important; opacity: 1 !important; }""",
) as interface:
    warning = gr.Button(
        "⚠️⚠️⚠️ CAUTION ⚠️⚠️⚠️", visible=False, interactive=False, elem_id="warning"
    )
    memory = gr.Textbox(
        value="",
        label="Important Information",
        interactive=False,
        elem_id="memory",
    )
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    msg.submit(process, [msg, chatbot], [msg, chatbot, memory])
    clear.click(lambda: None, None, chatbot, queue=False)

interface.launch()

# TODO: Generate comments, tests and error handling

import streamlit as st
from streamlit_chat import message
from termcolor import colored
from Agent import Agent

st.set_page_config(page_title="Ruby", page_icon="🦩")

print(st.session_state.to_dict())


def init():
    st.cache_data.clear()
    st.cache_resource.clear()


if "initialised" not in st.session_state or st.session_state["initialised"] is not True:
    print(colored("FIRST RUN. CLEARING CACHE.", "red"))
    init()
    st.session_state["initialised"] = True


def reset():
    print(colored("RESETTING. CLEARING CACHE.", "red"))
    st.cache_data.clear()
    st.cache_resource.clear()
    init()


@st.cache_resource(ttl=3600)
def init_therapist():
    assistant = Agent(
        config_path="./agents/therapist.toml", api_key=st.secrets.OPENAI_API_KEY
    )
    return assistant


therapist = init_therapist()
print(id(therapist))

if "message_history" not in st.session_state:
    st.session_state["message_history"] = [
        {"role": "assistant", "content": therapist.gambit}
    ]


def push_message(role: str = "user", content: str = ""):  # TODO: Decouple
    st.session_state["message_history"].append({"role": role, "content": content})


def chat_input_process():
    # therapist.load_config('./agents/therapist.toml')
    message = st.session_state.chat_input
    push_message(content=message)
    st.session_state.chat_input = ""

    with st.spinner(""):
        response = therapist.think(st.session_state["message_history"])

    print(response["response"], therapist.knowledge)

    push_message(role="assistant", content=response["response"])


if "message_history" not in st.session_state:
    st.session_state.message_history = []

for m in st.session_state.message_history:
    message(m["content"], True if m["role"] == "user" else False, avatar_style="shapes")
chat_input = st.text_input("Type here", key="chat_input", on_change=chat_input_process)
st.button("Restart", on_click=reset)
if therapist.concern:
    st.error("Child is potentially at risk. Intervention required.", icon="👩‍⚕️")
else:
    st.success("No cause for concern.", icon="👩‍⚕️")
st.info(f'Child autobiography: "{therapist.autobiography}"', icon="📖")

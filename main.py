import streamlit as st
from streamlit_chat import message
from Agent import Agent

if 'first_run' not in st.session_state:
    st.session_state['first_run'] = True

def init():
    st.cache_data.clear()
    st.session_state['message_history'] = [
        {"role": "assistant", "content": "Hi"}
    ]
    st.session_state.first_run = False

if st.session_state.first_run is True:
    init()
    

@st.cache_data
def init_therapist():
    return Agent(config_path="./agents/therapist.toml")

therapist = init_therapist()

def push_message(role:str = "user", content:str=""): # TODO: Decouple
    st.session_state['message_history'].append({"role":role, "content":content})

def chat_input_process():

    message = st.session_state.chat_input
    push_message(content=message)
    st.session_state.chat_input = ""

    therapist.think(message)
    push_message(role="assistant", content=therapist.latest['response'])


for m in st.session_state.message_history:
    message(m['content'], True if m['role']=='user' else False)
chat_input = st.text_input("Type here", key='chat_input', on_change=chat_input_process)
st.button("Restart", on_click=init)
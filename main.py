import streamlit as st
from streamlit_chat import message
from Agent import Agent

st.set_page_config(page_title="Ruby", page_icon="🦩")

if 'first_run' not in st.session_state:
    st.session_state['first_run'] = True

def init():
    st.cache_data.clear()
    st.session_state['message_history'] = [
        {"role": "assistant", "content": "Hi, I'm Ruby."}
    ]
    st.session_state.first_run = False

if st.session_state.first_run is True:
    init()
    

@st.cache_resource
def init_therapist():
    return Agent(config_path="./agents/therapist.toml", api_key=st.secrets.OPENAI_API_KEY)

therapist = init_therapist()
print(id(therapist))

def push_message(role:str = "user", content:str=""): # TODO: Decouple
    st.session_state['message_history'].append({"role":role, "content":content})

def chat_input_process():

    # therapist.load_config('./agents/therapist.toml')
    message = st.session_state.chat_input
    push_message(content=message)
    st.session_state.chat_input = ""

    with st.spinner(''):
        therapist.think(message)

    push_message(role="assistant", content=therapist.latest['response'])



for m in st.session_state.message_history:
    message(m['content'], True if m['role']=='user' else False, avatar_style="shapes")
chat_input = st.text_input("Type here", key='chat_input', on_change=chat_input_process)
st.button("Restart", on_click=init)

st.write(therapist.knowledge)
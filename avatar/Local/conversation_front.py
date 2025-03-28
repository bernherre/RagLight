# Source:Below code is provided by Streamlit and AWS 

#1 import streamlit and chatbot file
import streamlit as st 
import conversation_back as demo  #**Import your Chatbot file as demo
from transcribe import transcribe
from langchain_core.prompts import ChatPromptTemplate
from utilities import text_chat

#2 Set Title for Chatbot - https://docs.streamlit.io/library/api-reference/text/st.title
st.title("Hi, This is Chatbot Ax :sunglasses:") # **Modify this based on the title you want in want

#3 LangChain memory to the session cache - Session State - https://docs.streamlit.io/library/api-reference/session-state
if 'memory' not in st.session_state: 
    st.session_state.memory = demo.demo_memory() #** Modify the import and memory function() attributes initialize the memory
    
#4 Add the UI chat history to the session cache - Session State - https://docs.streamlit.io/library/api-reference/session-state
if 'chat_history' not in st.session_state: #see if the chat history hasn't been created yet
    initial_message={"role":"ai", "text":"I am a kind of 5 years with a deeper understanding on physics and mathematics. And I can explain the concept in a simplest way with similitudes for kids taking in account that you are talking with toddlers ever responding on spanish."}
    st.session_state.chat_history = [initial_message] #initialize the chat history

#5 Re-render the chat history (Streamlit re-runs this script, so need this to preserve previous chat messages)
for message in st.session_state.chat_history: 
    with st.chat_message(message["role"]): 
        st.markdown(message["text"]) 

#6 Enter the details for chatbot input box 
template = "you are a girl of 5 years with a deeper understanding on physics and mathematics. And you can explain the concept in a simplest way with similitudes for kids taking in account that you are talking with toddlers ever responding on spanish."
promp_template = ChatPromptTemplate([
                (
                         "ai",
                         "you are a girl of 5 years with a deeper understanding on physics and mathematics. And you explein the concept any in a simple way with similitudes normal like cars and unicorns for kids and girls toddlers ever responding on spanish."
                ),
                (
                        
                        "user",
                        "chat history:{input_text}"

                )
                ],template=template)
input_text = st.chat_input("Powered by Ollama") # **display a chat input box

text_chat(input_text,st,promp_template,demo)
    
#7 Enter audio box
audio_value = st.audio_input("Record a voice message")

if audio_value: 
    # Save the uploaded file to a temporary location
    input_text = transcribe(audio_value) # **display a chat input box
    text_chat(input_text,st,promp_template,demo)
    input_audio=st.audio(audio_value, format="audio/wav")
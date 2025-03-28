# Load a base LLM (e.g., GPT-2 or LLaMA)


from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain
# Import the required module for text 
# to speech conversion
from gtts import gTTS
#fechas
import datetime
import pygame

# This module is imported so that we can 
# play the converted audio
import os

#import playsound module to reproduce audio
#from playsound import playsound
import pygame


# Step 1: Initialize the Ollama model
def demo_chatbot():
    chat_model = ChatOllama(
        model="llama3.2:latest",
        temperature=0.8,
        num_predict=400)  
        # Replace with your Ollama model
    return chat_model

#2b Test out the LLM with Predict method instead use invoke method
    #return demo_llm.invoke(input_text)
#response=demo_chatbot(input_text="Hi, what is the temperature in new york in January?")
#print(response)

#3 Create a Function for  ConversationSummaryBufferMemory  (llm and max token limit)
def demo_memory():
    llm_data=demo_chatbot()
    memory=ConversationSummaryBufferMemory(llm=llm_data,max_token_limit=300)
    return memory

#4 Create a Function for Conversation Chain - Input text + Memory
def demo_conversation(input_text,memory):
    llm_chain_data=demo_chatbot()

    llm_conversation=ConversationChain(llm=llm_chain_data,memory=memory,verbose=True)

#5 Chat response using invoke (Prompt template)
    chat_reply=llm_conversation.invoke(input_text)
    return chat_reply['response']

#1 https://python.langchain.com/v0.1/docs/integrations/llms/bedrock/
#pip install -U langchain-aws
#pip install anthropic

# Load a base LLM (e.g., GPT-2 or LLaMA)


from typing import Literal

from langchain_core.messages import SystemMessage, RemoveMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
# Import the required module for text 
# to speech conversion
from gtts import gTTS
#fechas

import pygame

# This module is imported so that we can 
# play the converted audioes

#import playsound module to reproduce audio
#from playsound import playsound
import pygame
from io import BytesIO



# Step 0 : Set up chat memory  and message memory
memory= MemorySaver()

# We will add a `summary` attribute (in addition to `messages` key,
# which MessagesState already has)
class State(MessagesState):
    summary: str

# Step 1: Initialize the Ollama model
chat_model = ChatOllama(model="llama3.2:latest",temperature=0.8, num_predict=400)  # Replace with your Ollama model


# Step 2: Define the logic to call the model
def call_model(state: State):
    # If a summary exists, we add this in as a system message
    summary = state.get("summary", "")
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]
    response = chat_model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Step 3: We now define the logic for determining whether to end or summarize the conversation
def should_continue(state: State) -> Literal["summarize_conversation", END]:
    """Return the next node to execute."""
    messages = state["messages"]
    # If there are more than six messages, then we summarize the conversation
    if len(messages) > 6:
        return "summarize_conversation"
    # Otherwise we can just end
    return END

def summarize_conversation(state: State):
    # First, we summarize the conversation
    summary = state.get("summary", "")
    if summary:
        # If a summary already exists, we use a different system prompt
        # to summarize it than if one didn't
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = chat_model.invoke(messages)
    # We now need to delete messages that we no longer want to show up
    # I will delete all but the last two messages, but you can change this
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}
# Define a new graph
workflow = StateGraph(State)

# Define the conversation node and the summarize node
workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)

# Set the entrypoint as conversation
workflow.add_edge(START, "conversation")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `conversation`.
    # This means these are the edges taken after the `conversation` node is called.
    "conversation",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
)

# We now add a normal edge from `summarize_conversation` to END.
# This means that after `summarize_conversation` is called, we end.
workflow.add_edge("summarize_conversation", END)

# Finally, we compile it!
app = workflow.compile(checkpointer=memory)

def print_update(update):
    for k, v in update.items():
        for m in v["messages"]:
            m.pretty_print()
        if "summary" in v:
            print(v["summary"])



# Step 2: Define a prompt for query expansion
promp_template = ChatPromptTemplate([
                (
                         "system",
                         "you are a kind of 5 years with a deeper understanding on physics and mathematics. And you explein the concept any in a simple way with similitudes for kids taking in account that you are t<alking with toddlers."
                ),
                (
                        "user",
                        "{question}" 

                )
                ])


# Step 3: Create a chain for query expansion
expansion_chain = promp_template | chat_model| StrOutputParser()

def main():
    config = {"configurable": {"thread_id": "4"}}
    input_message = HumanMessage(content="hi! I'm bob")
    input_message.pretty_print()
    for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
        print_update(event)

    input_message = HumanMessage(content="what's my name?")
    input_message.pretty_print()
    for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
        print_update(event)

    input_message = HumanMessage(content="i like the celtics!")
    input_message.pretty_print()
    for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
        print_update(event)





"""def main():
    


    try:
        # Initialize the expander
        
        print("Welcome to LangChain Query Expander!")
        print("Enter a question to see different variations (or 'quit' to exit)")
        print("\nExample questions:")
        print("- How to use multi-modal models in a chain?")
        print("- What's the best way to stream events from an LLM agent?")
        print("- How to implement RAG with vector databases?")
        
        lang = input("\nen or es or de: ").strip()
        if lang == 'en':        
                        # Language in which you want to convert
            language = 'en'
        elif lang == 'es':        
            # Language in which you want to convert
            language = 'es'
        elif lang=='de':
            language='de'
        else:
            print("Please enter a valid language")
                    
        
        while True:
  
            if lang == 'en':        
                        # Language in which you want to convert
                        question = input("\nEnter your question: ").strip()
            if lang == 'es':        
                        # Language in which you want to convert
                        
                        question = input("\nDanos tu pregunta: ").strip()
            if lang == 'de':
                
                        question=input("\nBitte, stellt eine Frage: ").strip()

            #question = input("\nEnter your question: ").strip()
            
            if (question.lower() == 'quit') | (lang.lower() == 'quit'):
                print("Bye, bye!")
                break        

            else: 
                          
                if question in query_cache:
                    print("Cache hit!")
                    variation=expansion_chain.invoke({"question": question})
                    variation=variation.replace("*", " ")
                    print(variation)    

                    # Passing the text and language to the engine, 
                    # here we have marked slow=False. Which tells 
                    # the module that the converted audio should 
                    # have a high speed
                    myobj = gTTS(text=variation, lang=language, slow=False)

                    fp=bytesIO()
                    myobj.write_to_fp(fp)
                    fp.seek(0)
                    
                    # Playing the converted file
                    #os.system("start welcome.wav")

                    # Initialize the mixer module
                    pygame.mixer.init()

                    # Load the mp3 file
                    pygame.mixer.music.load(fp)

                    # Play the loaded mp3 file
                    pygame.mixer.music.play()
                    #for i, variation in enumerate(variations, 1):
                    #    print(f"\n{i}. {variation}")
            
                    #print("\nTotal variations generated:", len(variations)-1)
                
                else:     
                    
                    variation=expansion_chain.invoke({"question": question})
                    variation=variation.replace("*", " ")
                    print(variation)

                    # Passing the text and language to the engine, 
                    # here we have marked slow=False. Which tells 
                    # the module that the converted audio should 
                    # have a high speed
                    myobj = gTTS(text=variation, lang=language, slow=False)

                    fp=BytesIO()
                    myobj.write_to_fp(fp)
                    fp.seek(0)
                    
                    # Playing the converted file
                    #os.system("start welcome.wav")

                    # Initialize the mixer module
                    pygame.mixer.init()

                    # Load the mp3 file
                    pygame.mixer.music.load(fp)

                    # Play the loaded mp3 file
                    pygame.mixer.music.play()
                    
                    #print("\nTotal variations generated:", len(variations)-1)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please check your API key and try again.")"""

if __name__ == "__main__":
    main()
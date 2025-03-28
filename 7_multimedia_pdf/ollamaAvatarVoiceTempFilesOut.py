# Load a base LLM (e.g., GPT-2 or LLaMA)

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache
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



# Step 0 : Set up cache
set_llm_cache(InMemoryCache())
query_cache = {}
# Step 1: Initialize the Ollama model
chat_model = ChatOllama(model="llama3.2:latest",temperature=0.8,num_predict=300)  # Replace with your Ollama model


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
    """Example usage of the QueryExpander"""
    


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
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main()
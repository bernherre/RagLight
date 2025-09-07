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
chat_model = ChatOllama(model="llama3.2:latest", use_gpu=True,            # Explicitly enable GPU usage
    gpu_device=0 ,temperature=0.9, top_p=0.9, num_predict=12000)  # Replace with your Ollama model


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
                         "You are a literature teacher with deep knowledge, capable of enhancing texts by incorporating elements from various authors to engage readers emotionally. Your knowdledge of literature is vast, and you can draw from a wide range of authors to create a rich and engaging text. You are also capable of providing a summary of the text, highlighting its main themes and ideas ever in Spanish independing the language from the questions." 
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
    input_message = HumanMessage(content="hola! My nombre es bob")
    input_message.pretty_print()
    for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
        print_update(event)

    input_message = HumanMessage(content="Cuál es mi nombre?")
    input_message.pretty_print()
    for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
        print_update(event)

    message="""En las calles empedradas de Constanza, bajo el cielo plomizo del sur de Alemania, dos almas jóvenes se encontraban día a día, como si obedecieran una gravedad secreta que sólo las mentes llenas de conocimiento e inocencia entienden. Él, un joven de cabello castaño y ojos color miel, educado en la tradición católica, había llegado a estas tierras con una beca y un hambre de conocimiento que parecía no calmarse nunca. Ella, Ludmila, del este de Europa, rubia, delgada, con un rostro que a veces parecía hecho de nieve y a veces de fuego interior, había crecido soñando con la calidez que encontraba ahora en la forma en que él le servía el té, o la escuchaba con atención cuando hablaba de lo que fuere, desde filosofía pasando por historia, por dudas de la vida, por que comer o física y matemáticas.
Se conocieron en un seminario sobre el tiempo, entre ecuaciones y formulas difíciles de comprender, citas a Bergson. No se miraron mucho ese día, pero desde entonces se buscaron sin decirlo. Su mundo era de bibliotecas silenciosas, caminatas junto al Rin, la sobria y placida tranquilidad del Bodensee, paseos en invierno cuando el lago parecía de cristal quebrado, y veranos tan calurosos que se refugiaban en la biblioteca de la universidad sólo para sentir el aire fresco y la paz de estar uno junto al otro, aunque no se rozaran ni una vez los dedos.
Ludmila tenía un amor por el conocimiento que él encontraba cautivador. Marcada por una educación rigurosa y una vida sin adornos. Había llegado a Alemania con la esperanza de crecer, pero no esperaba encontrar ternura en un extraño, aceptaba que su cocina era maravillosa, y se esforzaba por siempre hacer algo cuando era su turno para deslumbrarlo a él, cocinar para los dos se convirtió en una carta de amor, llena de olor, de gusto.  Él la fascinaba con sus relatos sobre especias, sobre cómo se ablanda una berenjena con sal y paciencia. Sobre las especias que usaba Leonardo Da Vinci para sus pinturas y como aprendió a usarlas desde niño educado en una cocina.  A ella le conmovía esa calidez que en su tierra natal era escasa, casi una fantasía.
La Navidad llegó con su luz dorada y su aroma a especias. El mercado navideño junto al lago se llenó de pequeñas cabañas de madera, de vino caliente, de pan de jengibre, nueces caramelizadas, fondue suizo y de risas. Era una época especial, el transporte público vivía lleno día y noche, en los buses se veían desde estudiantes hasta personas mayores que iban y venían al mercado navideño, padres con sus hijos envueltos en los atavíos más abrigados y llorando en una mezcla de cansancio y felicidad, pero disfrutando esos pocos días donde el mercado es para ricos, pobres extranjeros y locales por igual.  Un día, entre luces colgantes y el reflejo del lago helado, Ludmila y él compartieron un vaso de Glühwein, unas nueces caramelizadas y un par de sonrisas que simulaban más que una constante y cálida compañía. No se dijeron lo que sentían, pero sus miradas hablaban de una intimidad muda. Él le compró una pequeña figura de madera, una estrella tallada a mano. Ella sonrió y bajó la mirada. Esa estrella aún vive en alguna caja, en algún rincón, como testimonio de todo lo que no se dijo, y un pequeño regalo de despedida en español que se ha intentado traducir a idiomas eslavos para cada día intentando soñar mas.
Caminaban mucho. Por los senderos cerca de Mainau, por el Egg en los bosques, viendo en otoño y primavera los animales libres, y hasta uno que otro zorro; caminaron incalculable número de veces por el casco antiguo de la ciudad, donde las paredes parecían contar historias de siglos. Fueron a las calles donde a un lado era Kreuzlingen y al otro Constanza para pasar de Suiza a Alemania y de Alemania a Suiza.  A veces hablaban de ciencia, otras de lo efímero del tiempo. Nunca se tocaron, salvo algún roce accidental al compartir un libro o al sentarse demasiado cerca en el paradero del Bus. Pero cada silencio compartido era un poema sin escribir.
Un verano, se sentaron en el césped junto al Sporthalle de la universidad, en un rincón donde siempre daba sombra. Él le leyó en voz alta a Heine. Ella escuchó con los ojos cerrados, como si aquellas palabras fueran agua fresca en un día de calor. Ese momento quedó suspendido, detenido en un equilibrio perfecto, como todo lo que vivieron juntos. Muchas veces le enviaba o leía a Borges, Silva, Neruda, y aunque ella no entendía la mayoría sumergía en el momento y recordaba cada expresión, con el tono y la calidez que él emanaba. 
Y sin embargo, nada cambió. O todo lo hizo en secreto.
Un día, sin aviso, él volvió a su país. No hubo despedida. Tal vez por miedo, tal vez por pudor. Tal vez porque los amores que viven sólo en la posibilidad no soportan la realidad de un adiós. Ludmila se enteró por un correo breve, una línea cordial, o un poco más. Él no mencionó sus tardes en la biblioteca ni los paseos bajo la nieve. Pero tal vez no hacía falta.
Desde entonces, cuando el invierno vuelve y el mercado navideño abre sus luces frente al lago, Ludmila camina sola por los mismos puestos. A veces cree ver unos ojos color miel entre la multitud. No se detiene. Pero en su corazón, cada aroma a canela, cada copo de nieve, es un recuerdo de aquel casi-amor, de aquel muchacho que hablaba de física como si recitara poesía, y la miraba como si ella fuera la única ecuación que aún no lograba resolver.
 """
    input_message = HumanMessage(content="Cómo harías más bello este texto incluyendo elementos que envuelvan al lector :"+message)
    input_message.pretty_print()
    for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
        print_update(event)
    input_message = HumanMessage(content="Puedes crear un parrafo adicional donde Ludmila en el tiempo libre aprenda español  :"+message)
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
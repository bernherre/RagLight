# Load a base LLM (e.g., GPT-2 or LLaMA)

from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache



# Step 0 : Set up cache
set_llm_cache(InMemoryCache())
query_cache = {}
# Step 1: Initialize the Ollama model
chat_model = ChatOllama(model="llama3.2:latest")  # Replace with your Ollama model


# Step 2: Define a prompt for query expansion
promp_template = ChatPromptTemplate([
                (
                         "system",
                         "you are a kind of 5 years with a deeper understanding on physics and mathematics. And you explein the concept any in a simple way with similitudes for kids."
                ),
                (
                        "user",
                        "List[str]: List of paraphrased variations of the question : {question}" 

                )
                ])
# Step 3: Create a chain for query expansion
expansion_chain = promp_template | chat_model| StrOutputParser()

# Step 4: Define a function to refine the expanded query
def refine_expansion(output: str) -> str:
    # Remove unnecessary text and clean up the output
    expanded_terms = output.strip().split("\n")
    expanded_terms =[term.strip() for term in expanded_terms if term.strip()]
    #eval(output.strip().split("# Output:")[1])
   # [term.strip() for term in expanded_terms if term.strip()]
    return expanded_terms



# Step 5: Create the full pipeline
def query_expansion_pipeline(query: str) -> str:
    # Generate expanded terms
    
    expansion_output = expansion_chain.invoke(query)
    # Refine the output
    refined_expansion = refine_expansion(expansion_output)
    return  refined_expansion

"""    # Step 6: Test the pipeline
    query = "what is rag"
    expanded_query = query_expansion_pipeline(query)
    print(f"Original Query: {query}")
    print(f"Expanded Query: {expanded_query}")"""

"""def query_expansion_pipeline(query: str, context: str) -> str:
    # Generate expanded terms
    expansion_output = expansion_chain.run(query=query, context=context)
    # Refine the output
    expanded_terms = refine_expansion(expansion_output).split(", ")
    # Filter terms based on context
    filtered_terms = filter_terms(expanded_terms, context)
    return ", ".join(filtered_terms)"""



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
        
        while True:
            question = input("\nEnter your question: ").strip()
            
            if question.lower() == 'quit':
                print("Thank you for using LangChain Query Expander. Goodbye!")
                break
                
          

            else: 
                          
                if question in query_cache:
                    print("Cache hit!")
                    variation=query_cache[question]["paraphrased_queries"]
                    for i, variation in enumerate(variations, 1):
                        print(f"\n{i}. {variation}")
            
                    print("\nTotal variations generated:", len(variations)-1)
                
                else:     

                    expanded_query = query_expansion_pipeline(question)
                    variations = [result for result in expanded_query]
                    print("\nGenerating variations...")
                    #query = "machine learning" 
                    query_cache[question] = {
                        "paraphrased_queries": variations
                    }
            
                    print("\nExpanded Queries:")
                    for i, variation in enumerate(variations, 1):
                        print(f"{variation}")
            
                    print("\nTotal variations generated:", len(variations)-1)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main()
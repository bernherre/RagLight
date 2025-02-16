import os
import numpy as np
from langchain.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
#from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from transformers import LlamaForCausalLM, LlamaTokenizer

from llamaapi import LlamaAPI
from langchain_experimental.llms import ChatLlamaAPI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain import PromptTemplate, LLMChain
from langchain.llms import HuggingFacePipeline
import torch
from langchain.embeddings.huggingface import HuggingFaceBgeEmbeddings
from llama_index.core import Settings



# Configuration variables
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
MAX_TOKENS = 15000
MODEL_NAME = "zephyr-7b-alpha"
TEMPERATURE = 0.1

# Set up OpenAI API key
LLAMA_API_KEY = os.environ.get("LLAMA_API_KEY")
if not LLAMA_API_KEY:
    LLAMA_API_KEY = input("Please enter your LlamaAI API key: ")
    os.environ["LLAMA_API_KEY"] = LLAMA_API_KEY


def load_csv_data(file_path):
    loader = CSVLoader(file_path=file_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from CSV")
    return documents

def create_embeddings(documents):
    text_splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} chunks")

    #embeddings = OpenAIEmbedding()
    #Settings.embed_model = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-base-en")
    
    
    model_name = "BAAI/bge-small-en"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": True}
    embeddings = HuggingFaceBgeEmbeddings(
            model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)
    # Print sample embedding
    if texts:
        sample_text = texts[0].page_content
        sample_embedding = embeddings.embed_query(sample_text)
        print("\nSample Text:")
        print(sample_text)
        print("\nSample Embedding (first 10 dimensions):")
        print(np.array(sample_embedding[:10]))
        print(f"\nEmbedding shape: {np.array(sample_embedding).shape}")

    return texts, embeddings

def create_vectorstore(texts, embeddings):
    vectorstore = FAISS.from_documents(texts, embeddings)
    return vectorstore

def setup_qa_chain(vectorstore):
    
    # Load the tokenizer and model
    tokenizer = LlamaTokenizer.from_pretrained("C:\\Users\\bernh\\AppData\\Local\\Programs\\Ollama\\")
    model = LlamaForCausalLM.from_pretrained("C:\\Users\\bernh\\AppData\\Local\\Programs\\Ollama\\")

    # Move the model to GPU if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
# Create a pipeline using the LLaMA model
    pipeline = HuggingFacePipeline(
    model=model,
    tokenizer=tokenizer,
    device=device,
    model_kwargs={"temperature": 0.7, "max_length": 512}
)

    
    
    # Set up LlamaAI language model

# Replace 'Your_API_Token' with your actual API token



    PROMPT = PromptTemplate(
        input_variables=["question"],
        template="Answer the following question: {question}"
    )

# Create a RetrievalQA chain
    retriever = vectorstore.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(
        llm=pipeline,
        chain_type="stuff",
        retriever=retriever
    )

    return qa_chain

def process_query(query, qa_chain):
    result = qa_chain({"query": query})
    return result['result'], result['source_documents']

def main():
    print("Welcome to the CSV RAG Pipeline!")
    
    csv_path = input("Please enter the path to your CSV file: ")
    
    print("Loading and processing CSV data...")
    documents = load_csv_data(csv_path)
    
    print("Creating embeddings...")
    texts, embeddings = create_embeddings(documents)
    
    print("Creating vector store...")
    vectorstore = create_vectorstore(texts, embeddings)
    
    print("Setting up QA chain...")
    qa_chain = setup_qa_chain(vectorstore)
    
    print("\nRAG Pipeline initialized. You can now ask questions about your CSV data.")
    print("Enter 'quit' to exit the program.")
    
    while True:
        query = input("\nEnter your question: ")
        if query.lower() == 'quit':
            print("Exiting the program. Goodbye!")
            break
        
        answer, sources = process_query(query, qa_chain)
        print(f"\nAnswer: {answer}")
        print("\nSources:")
        for source in sources:
            print(f"- {source.page_content[:100]}...")

if __name__ == "__main__":
    main()
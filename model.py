import os
import chromadb
import shutil
import openai
import sys
import numpy as np
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain

def getResponse(question: str, chat_history) -> str:

    embedding = OpenAIEmbeddings()

    # Load the API keys from the .env file
    load_dotenv('./.env')
    db_directory = "./docs/vectordb"
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

    # Load an existing Chroma vector store
    vectordb = Chroma(persist_directory=db_directory, embedding_function=embedding)
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key='question', 
        output_key='answer'
    )

    # Define template prompt
    template = """You are a friendly chatbot that helps HealthServe employees for onboarding process and handle day-to-day work serving migrant workers in Singapore. Use the following pieces of context to answer the question at the end. 
    {context}
    Question: {question}
    Helpful Answer in english:
    Helpful Answer in tamil:
    Helpful Answer in bengali:
    Helpful Answer in Mandarin:"""

    your_prompt = PromptTemplate.from_template(template)

    # Define llm model
    llm_name = "gpt-3.5-turbo-16k"
    llm = ChatOpenAI(model_name=llm_name, temperature=0)

    # Define parameters for retrival
    retriever=vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 10})

    # Execute chain
    qa = ConversationalRetrievalChain.from_llm(
        llm,
        combine_docs_chain_kwargs={"prompt": your_prompt},
        retriever=retriever,
        return_source_documents=True,
        return_generated_question=True,
        # memory=memory,
    )

    # Enable tracing
    print("Enabling tracing...")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.langchain.plus"
    os.environ["LANGCHAIN_PROJECT"] = "Serve Ready Chatbot"
    
    # Evaluate your chatbot with questions
    result = qa({"question": question, "chat_history": chat_history})

    print(result)

    return { 
        "answer": result['answer'],
        "source_documents": result['source_documents'],
    }

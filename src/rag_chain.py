import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.llms import HuggingFacePipeline
from langchain_huggingface import HuggingFaceEmbeddings

# Load the API key from env variables
load_dotenv()

# api_key = os.getenv('OPENAI_API_KEY')


RAG_PROMPT_TEMPLATE = """
You are a helpful coding assistant that can answer questions about the provided context. The context is usually a PDF document or an image (screenshot) of a code file. Augment your answers with code snippets from the context if necessary.

If you don't know the answer, say you don't know.

Context: {context}
Question: {question}
"""
PROMPT = PromptTemplate.from_template(RAG_PROMPT_TEMPLATE)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def create_rag_chain(chunks):
    # embeddings = OpenAIEmbeddings(api_key=api_key)  #Use HuggingFaceEmbeddings instead
    embeddings = HuggingFaceEmbeddings()
    doc_search = FAISS.from_documents(chunks, embeddings)
    retriever = doc_search.as_retriever(
        search_type="similarity", search_kwargs={"k": 2}  #Find only the 2 most relevant chunks.
    )
    # llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)  # Use a free model
    llm = HuggingFacePipeline.from_model_id(
        model_id='distilgpt2',
        task='text-generation'
    )

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | PROMPT
        | llm
        | StrOutputParser()
    )

    return rag_chain



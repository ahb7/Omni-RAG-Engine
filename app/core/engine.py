import os
from operator import itemgetter
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

def format_docs(docs):
    """
    Safely converts a list of Document objects into a single string.
    This prevents the 'dict object has no attribute replace' error.
    """
    if not docs:
        return ""
    return "\n\n".join(doc.page_content for doc in docs)

class RAGEngine:
    def __init__(self):
        # This sends an API network request instead of running locally (Uses almost 0 RAM)
        self.embeddings = HuggingFaceEndpointEmbeddings(
            huggingfacehub_api_token=os.getenv("HF_TOKEN"),
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # High-performance inference via Groq
        self.llm = ChatGroq(
            temperature=0, 
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        
        self.vector_store_path = "vector_store/faiss_index"
        self.vector_store = None

    def ingest_pdf(self, chunks):
        """Vectorizes chunks and persists them to a local FAISS index"""
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        os.makedirs("vector_store", exist_ok=True)
        self.vector_store.save_local(self.vector_store_path)

    def get_answer(self, query: str, chat_history: list):
        """
        Executes a context-aware RAG chain. 
        Uses itemgetter to explicitly route data and avoid type mismatches.
        """
        # Load local index if it exists and isn't already in memory
        if not self.vector_store and os.path.exists(self.vector_store_path):
            self.vector_store = FAISS.load_local(
                self.vector_store_path, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )

        if not self.vector_store:
            return "No document found. Please upload a PDF first."

        # Template setup with history and context placeholders
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Omni-RAG Engine. Answer based only on the provided context."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("system", "Context: {context}"),
            ("human", "{question}"),
        ])

        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        # --- CONTEXT-AWARE LCEL CHAIN ---
        # itemgetter pulls specific keys from the input dictionary.
        # This ensures the retriever gets a string and the prompt gets formatted text.
        chain = (
            {
                "context": itemgetter("question") | retriever | format_docs,
                "question": itemgetter("question"),
                "chat_history": itemgetter("chat_history"),
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return chain.invoke({
            "question": query, 
            "chat_history": chat_history
        })



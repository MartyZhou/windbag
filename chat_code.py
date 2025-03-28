import json
import re
import os
import shutil
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language

class ChatCode:
    chain = None

    def __init__(self, use_online_model=False):
        load_dotenv()

        if use_online_model:
            # self.model = ChatOpenAI(
            #     model="gpt-4",
            #     temperature=0.7,
            #     max_tokens=4096,
            #     api_key=os.getenv("OPENAI_API_KEY")
            # )
            self.model = ChatOpenAI(
                model_name = os.getenv("MODEL_NAME"),
                # model="gpt-4",
                temperature = 0.7,
                max_tokens = 4096,
                openai_api_base = os.getenv("AI_GATEWAY_URL"),
                openai_api_key = os.getenv("AI_GATEWAY_API_KEY")
            )
        else:
            self.model = ChatOllama(model="codellama")

        self.prompt = PromptTemplate.from_template(
        """
        <s> [INST] You are an expert programmer specializing in debugging and troubleshooting code issues. 
        Your task is to analyze the provided context and answer the given question. 
        If applicable, provide a solution and the relevant code snippet in the following format:

        Summary:

        Code Snippet for Solution (limit to the relevant part of the code):
        ```php
        code
        ```

        Original code snippet (limit to the relevant part of the code):
        ```php
        code
        ```

        If you are not confident in your answer, respond with "I don't know."
        [/INST] </s> 
        [INST] Question: {question} 
        Context: {context} 
        Answer: [/INST]
        """
    )

    def ingest(self, path: str, persist_directory: str = "chroma_db"):
        MAX_TOKENS = 512

        if os.path.exists(persist_directory):
            shutil.rmtree(persist_directory)
            print(f"Deleted existing persist directory: {persist_directory}")

        loader = GenericLoader.from_filesystem(
            path,
            glob="**/[!.]*",
            suffixes=[".php"],
            parser=LanguageParser(),
            exclude=["vendor/**", "storage/**"]
        )

        documents = loader.load()
        for doc in documents:
            doc.metadata["file_path"] = doc.metadata.get("source", "unknown")

        text_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PHP,
            chunk_size=MAX_TOKENS,
            chunk_overlap=10
        )

        chunks = text_splitter.split_documents(documents)
        chunks = filter_complex_metadata(chunks)

        vector_store = Chroma.from_documents(
            documents=chunks, 
            embedding=FastEmbedEmbeddings(),
            persist_directory=persist_directory
        )

        retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 1, "score_threshold": 0.5}
        )

        self.retriever = retriever

        self.chain = ({"context": retriever, "question": RunnablePassthrough()}
                      | self.prompt
                      | self.model
                      | StrOutputParser())
        
        print(f"Ingested {len(documents)} documents from {path}")

    def ask(self, query: str):
        if not self.chain:
            return json.dumps({"error": "Please, add a directory first."}) 
        
        file_paths = []
        full_context = ""
        if hasattr(self, "retriever") and self.retriever:
            search_results = self.retriever.invoke(query)
            file_paths = [doc.metadata.get("file_path", "unknown") for doc in search_results]

        for file_path in file_paths:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    full_context += file.read() + "\n"
            except Exception as e:
                full_context += f"Error reading file {file_path}: {e}\n"

        result = self.chain.invoke({"context": full_context, "question": query})


        code_snippet = None
        code_match = re.search(r"```php(.*?)```", result, re.DOTALL)
        if code_match:
            code_snippet = code_match.group(1).strip()

        return json.dumps({
            "response": result,
            "file_paths": file_paths,
            "code_snippet": code_snippet
        })

    def clear(self):
        self.chain = None


    def load(self, persist_directory: str = "chroma_db"):
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=FastEmbedEmbeddings()
        )
        self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 1, "score_threshold": 0.5}
        )

        self.chain = ({"context": self.retriever, "question": RunnablePassthrough()}
                    | self.prompt
                    | self.model
                    | StrOutputParser())

        print(f"RAG pipeline loaded from {persist_directory}")
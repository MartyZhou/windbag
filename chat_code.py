import json
import re
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
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

    def __init__(self):
        self.model = ChatOllama(model="codellama")
        self.prompt = PromptTemplate.from_template(
        """
        <s> [INST] You are an expert programmer specializing in debugging and troubleshooting code issues. 
        Your task is to analyze the provided context and answer the given question. 
        If applicable, provide a solution and the relevant code snippet in the following format:

        Summary:

        Original code snippet:
        ```php
        code
        ```

        Code Snippet for Solution:
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

    def ask(self, query: str):
        if not self.chain:
            return json.dumps({"error": "Please, add a directory first."}) 
        
        result = self.chain.invoke(query)

        file_paths = []
        if hasattr(self, "retriever") and self.retriever:
            search_results = self.retriever.invoke(query)
            file_paths = [doc.metadata.get("file_path", "unknown") for doc in search_results]

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
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
        self.model = ChatOllama(model="codellama:13b")
        self.prompt = PromptTemplate.from_template(
        """
        <s> [INST] You are an expert programmer specializing in debugging and troubleshooting code issues. 
        Your task is to analyze the provided context and answer the given question. 
        If applicable, provide a solution and the relevant code snippet in the following format:

        Summary:
        ```php
        solution
        ```

        Code Snippet:
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
        
        loader = GenericLoader.from_filesystem(
            path,
            glob="**/[!.]*",
            suffixes=[".php"],
            parser=LanguageParser(),
            exclude=["**/vendor/**", "**/storage/**"]
        )

        documents = loader.load()
        for doc in documents:
            # print(doc)  # Print the document to see its structure
            # print(doc.metadata)  # Print the metadata to see its structure
            doc.metadata["file_path"] = doc.metadata.get("source", "unknown")

        text_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PHP,
            chunk_size=1024,
            chunk_overlap=100
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
            search_kwargs={"k": 5, "score_threshold": 0.5}
        )

        self.retriever = retriever

        self.chain = ({"context": retriever, "question": RunnablePassthrough()}
                      | self.prompt
                      | self.model
                      | StrOutputParser())

    def ask(self, query: str):
        if not self.chain:
            return json.dumps({"error": "Please, add a directory first."})  # Return JSON error message

        # Invoke the chain and get the result
        result = self.chain.invoke(query)

        # Retrieve file paths from the retriever's documents
        file_paths = []
        if hasattr(self, "retriever") and self.retriever:
            search_results = self.retriever.invoke(query)  # Use invoke instead of get_relevant_documents
            file_paths = [doc.metadata.get("file_path", "unknown") for doc in search_results]

        code_snippet = None
        code_match = re.search(r"```php(.*?)```", result, re.DOTALL)
        if code_match:
            code_snippet = code_match.group(1).strip()

        # Convert the result to JSON format with file paths
        return json.dumps({
            "response": result,
            "file_paths": file_paths,
            "code_snippet": code_snippet
        })

    def clear(self):
        self.chain = None


    def load(self, persist_directory: str = "chroma_db"):
        """Load the RAG pipeline components from the persistent vector store."""
        # Load the persistent vector store
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=FastEmbedEmbeddings()
        )
        self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 5, "score_threshold": 0.5}
        )

        # Reconstruct the chain
        self.chain = ({"context": self.retriever, "question": RunnablePassthrough()}
                    | self.prompt
                    | self.model
                    | StrOutputParser())

        print(f"RAG pipeline loaded from {persist_directory}")
import os
from chat_code import ChatCode

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["LANGCHAIN_TRACING_V2"] = ""

code = ChatCode()

print("Starting ingestion...")
code.ingest("C:\\code\\semicolons\\php-code-base-for-rag")
print("Ingestion completed.")
response = code.ask("what language was this code base written in?")
print(response)

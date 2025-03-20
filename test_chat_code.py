import os
from chat_code import ChatCode
from tree_sitter_languages import get_language, get_parser

# try:
#     language = get_language('python')
#     parser = get_parser('python')
#     print("Successfully retrieved language:", language)
# except Exception as e:
#     print("Error:", e)
# os.environ["LANGCHAIN_HANDLER"] = ""
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["LANGCHAIN_TRACING_V2"] = ""
# os.environ["LANGCHAIN_TRACING"] = ""

code = ChatCode()

print("Starting ingestion...")
code.ingest("C:\\code\\semicolons\\sample_code")
code.ingest("C:\\code\\semicolons\\sample_code\\monolog-loki")
code.ingest("C:\\code\\semicolons\\laravel-crm")
print("Ingestion completed.")
response = code.ask("what language was this code base written in?")
print(response)

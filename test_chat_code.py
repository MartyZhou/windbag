import os
from chat_code import ChatCode

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["LANGCHAIN_TRACING_V2"] = ""

code = ChatCode(True)

# code.load()

test_php_repo_path = "C:\\code\\semicolons\\php-code-base\\monolog-loki"
code.ingest(test_php_repo_path)


response = code.ask("Provide code to fix the error log: Connection timed out after 128 milliseconds {'exception':'[object] (RuntimeException(code: 0): Curl error (code 28): Connection timed out after 128 milliseconds at monolog\\monolog\\src\\Monolog\\Handler\\Curl\\Util.php:54)[stacktrace]#0 itspire\\monolog-loki\\src\\main\\php\\Handler\\LokiHandler.php(151): Monolog\\Handler\\Curl\\Util::execute()#1 itspire\\monolog-loki\\src\\main\\php\\Handler\\LokiHandler.php(163): Itspire\\MonologLoki\\Handler\\LokiHandler->sendPacket()#2 monolog\\monolog\\src\\Monolog\\Handler\\AbstractProcessingHandler.php(44): Itspire\\MonologLoki\\Handler\\LokiHandler->write()#3 monolog\\monolog\\src\\Monolog\\Logger.php(391): Monolog\\Handler\\AbstractProcessingHandler->handle()... {main}'}")

print(response)

import os
from chat_code import ChatCode

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["LANGCHAIN_TRACING_V2"] = ""

code = ChatCode(False)

code.load()

# test_php_repo_path = "C:\\code\\semicolons\\code-for-rag\\laravel-crm"
# code.ingest(test_php_repo_path)


# response = code.ask("Provide code to fix the error log: Connection timed out after 128 milliseconds {'exception':'[object] (RuntimeException(code: 0): Curl error (code 28): Connection timed out after 128 milliseconds at monolog\\monolog\\src\\Monolog\\Handler\\Curl\\Util.php:54)[stacktrace]#0 itspire\\monolog-loki\\src\\main\\php\\Handler\\LokiHandler.php(151): Monolog\\Handler\\Curl\\Util::execute()#1 itspire\\monolog-loki\\src\\main\\php\\Handler\\LokiHandler.php(163): Itspire\\MonologLoki\\Handler\\LokiHandler->sendPacket()#2 monolog\\monolog\\src\\Monolog\\Handler\\AbstractProcessingHandler.php(44): Itspire\\MonologLoki\\Handler\\LokiHandler->write()#3 monolog\\monolog\\src\\Monolog\\Logger.php(391): Monolog\\Handler\\AbstractProcessingHandler->handle()... {main}'}")

response = code.ask("Provide code to fix the error log: Error updating activity {'activity_id':18,'error':'Undefined variable $personId','stack_trace':'#0 laravel-crm\\vendor\\laravel\\framework\\src\\Illuminate\\Foundation\\Bootstrap\\HandleExceptions.php(255): Illuminate\\Foundation\\Bootstrap\\HandleExceptions->handleError()  #1 laravel-crm\\packages\\Webkul\\Activity\\src\\Repositories\\ActivityRepository.php(100): Illuminate\\Foundation\\Bootstrap\\HandleExceptions->{closure:Illuminate\\Foundation\\Bootstrap\\HandleExceptions::forwardsTo():254}()  #2 laravel-crm\\packages\\Webkul\\Admin\\src\\Http\\Controllers\\Activity\\ActivityController.php(145): Webkul\\Activity\\Repositories\\ActivityRepository->update()  #3 laravel-crm\\vendor\\laravel\\framework\\src\\Illuminate\\Routing\\Controller.php(54): Webkul\\Admin\\Http\\Controllers\\Activity\\ActivityController->update()  #4 laravel-crm\\vendor\\laravel\\framework\\src\\Illuminate\\Routing\\ControllerDispatcher.php(43): Illuminate\\Routing\\Controller->callAction()  #5 laravel-crm\\vendor\\laravel\\framework\\src\\Illuminate\\Routing\\Route.php(259): Illuminate\\Routing\\ControllerDispatcher->dispatch()  #6 laravel-crm\\vendor\\laravel\\framework\\src\\Illuminate\\Routing\\Route.php(205): Illuminate\\Routing\\Route->runController()")

print(response)

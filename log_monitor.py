import json
import time
import re
import os
from dotenv import load_dotenv
from chat_code import ChatCode
from code_file_handler import replace_php_method
from github_repo import GitHubRepo

class LogMonitor:
    def __init__(self, log_file_path, chat_code_instance):
        self.log_file_path = log_file_path
        self.chat_code = chat_code_instance
        self.last_position = 0  # Track the last read position in the log file


    # sample error log: [2025-03-22 14:46:14] local.ERROR: Error updating activity {"activity_id":18,"error":"Undefined variable $personId","stack_trace":"#0 C:\\code\\semicolons\\php-code-base\\laravel-crm\\vendor\\laravel\\framework\\src\\Illuminate\\Foundation\\Bootstrap\\HandleExceptions.php(255): Illuminate\\Foundation\\Bootstrap\\HandleExceptions->handleError()
    # #1 C:\\code\\semicolons\\php-code-base\\laravel-crm\\packages\\Webkul\\Activity\\src\\Repositories\\ActivityRepository.php(100): Illuminate\\Foundation\\Bootstrap\\HandleExceptions->{closure:Illuminate\\Foundation\\Bootstrap\\HandleExceptions::forwardsTo():254}()
    # #2 C:\\code\\semicolons\\php-code-base\\laravel-crm\\packages\\Webkul\\Admin\\src\\Http\\Controllers\\Activity\\ActivityController.php(145): Webkul\\Activity\\Repositories\\ActivityRepository->update()
    # #3 C:\\code\\semicolons\\php-code-base\\laravel-crm\\vendor\\laravel\\framework\\src\\Illuminate\\Routing\\Controller.php(54): Webkul\\Admin\\Http\\Controllers\\Activity\\ActivityController->update()
    # #4 C:\\code\\semicolons\\php-code-base\\laravel-crm\\vendor\\laravel\\framework\\src\\Illuminate\\Routing\\ControllerDispatcher.php(43): Illuminate\\Routing\\Controller->callAction()
    # #5 C:\\code\\semicolons\\php-code-base\\laravel-crm\\vendor\\laravel\\framework\\src\\Illuminate\\Routing\\Route.php(259): Illuminate\\Routing\\ControllerDispatcher->dispatch()
    # #6 C:\\code\\semicolons\\php-code-base\\laravel-crm\\vendor\\laravel\\framework\\src\\Illuminate\\Routing\\Route.php(205): Illuminate\\Routing\\Route->runController()
    # #7 C:\\code\\semicolons\\php-code-base\\laravel-crm\\vendor\\laravel\\framework\\src\\Illuminate\\Routing\\Router.php(806): Illuminate\\Routing\\Route->run()
    # #8 C:\\code\\semicolons\\php-code-base\\laravel-crm\\vendor\\laravel\\framework\\src\\Illuminate\\Pipeline\\Pipeline.php(144): Illuminate\\Routing\\Router->{closure:Illuminate\\Routing\\Router::runRouteWithinStack():805}()

    def monitor_logs(self):
        print(f"Monitoring logs at: {self.log_file_path}")
        while True:
            try:
                with open(self.log_file_path, "r", encoding="utf-8") as log_file:
                    log_file.seek(self.last_position)

                    new_lines = log_file.readlines()
                    self.last_position = log_file.tell()

                    error_log = ""
                    for line in new_lines:
                        if self.is_error_log(line):
                            if error_log:  # Process the previous error log if it exists
                                self.handle_error(error_log.strip())
                                error_log = ""
                            error_log = line  # Start a new error log
                        elif error_log and self.is_stack_trace_line(line):  # Append stack trace lines
                            error_log += line
                        elif error_log:  # End of stack trace, process the error log
                            self.handle_error(error_log.strip())
                            error_log = ""

                    if error_log:  # Process the last error log if it exists
                        self.handle_error(error_log.strip())

            except FileNotFoundError:
                print(f"Log file not found: {self.log_file_path}")
            except Exception as e:
                print(f"Error while monitoring logs: {e}")

            time.sleep(2)

    def is_error_log(self, line):
        """Check if the log line starts with a timestamp and contains 'local.ERROR:'."""
        return re.match(r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] local\.ERROR:", line) is not None
    
    def is_stack_trace_line(self, line):
        """Check if the log line is part of a stack trace."""
        return re.match(r"^#\d+ ", line) is not None

    def handle_error(self, error_log):
        """Handle the detected error log by calling ChatCode.ask."""
        try:
            error_message, stack_trace = self.parse_error_log(error_log)
            print(f"Error Message: {error_message}")
            print(f"Stack Trace (first 3 lines):\n{stack_trace}")

            query = f"Provide code to fix the error log: {error_message}\nStack Trace:\n{stack_trace}"
            response = self.chat_code.ask(query)
            print(f"ChatCode Response: {response}")
            response_data = json.loads(response)  # Ensure the response is in JSON format
            file_path = response_data.get("file_paths")[0]            
            new_method_content = response_data.get("code_snippet")
            method_name = new_method_content.split("(")[0]  # Extract the method name from the code snippet

            if file_path and method_name and new_method_content:
                replace_php_method(file_path, method_name, new_method_content)
                self.create_pull_request(file_path, method_name, error_message, stack_trace)
            else:
                print("Invalid response format. Missing file_path, method_name, or new_method_content.")

        except Exception as e:
            print(f"Error while calling ChatCode: {e}")

    def parse_error_log(self, error_log):
        """Parse the error log to extract the error message and first 3 stack trace lines."""
        error_message_match = re.search(r"local\.ERROR: (.+?)stack_trace", error_log, re.DOTALL)
        error_message = error_message_match.group(1).strip() if error_message_match else "Unknown error"

        stack_trace_match = re.findall(r"#\d+ .+", error_log)
        base_path_pattern = r"C:\\code\\semicolons\\php-code-base\\laravel-crm\\"
        cleaned_stack_trace = [
            re.sub(base_path_pattern, "", line) for line in stack_trace_match[:3]
        ]

        error_message = error_message_match.group(1) if error_message_match else "Unknown error"

        stack_trace = "\n".join(cleaned_stack_trace) if cleaned_stack_trace else "No stack trace available"

        return error_message, stack_trace
    
    def create_pull_request(self, file_path, method_name, error_message, stack_trace):
        load_dotenv()
        github_token = os.getenv("GITHUB_TOKEN")
        repo_name = "octoobservo/laravel-crm"
        github_repo = GitHubRepo(github_token, repo_name)

        timestamp = time.strftime("%Y%m%d%H%M%S")
        branch_name = f"fix/{method_name.replace(' ', '_').lower()}_{timestamp}"
        commit_message = f"Fix for {method_name}"
        pr_title = f"Fix: {method_name} ({timestamp})"
        pr_body = f"This pull request fixes the issue detected in the method `{method_name}`.\n\nError Message:\n{error_message}\n\nStack Trace:\n{stack_trace}"

        github_repo.commit_and_create_pr(branch_name, file_path, commit_message, pr_title, pr_body)


if __name__ == "__main__":
    log_file_path = "C:\\code\\semicolons\\php-code-base\\laravel-crm\\storage\\logs\\laravel.log"

    chat_code = ChatCode(use_online_model=True)
    chat_code.load()

    log_monitor = LogMonitor(log_file_path, chat_code)
    log_monitor.monitor_logs()
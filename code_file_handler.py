def replace_php_method(file_path, method_name, new_method_content):
    """
    Replace a specific PHP method in a file with new content, preserving indentation.

    :param file_path: Path to the PHP file.
    :param method_name: The name of the PHP method to replace.
    :param new_method_content: The new content to replace the method with (including the method signature).
    """
    try:
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Find the method to replace
        in_method = False
        brace_count = 0
        updated_lines = []
        method_start_pattern = f"{method_name}("
        for line in lines:
            if method_start_pattern in line and not in_method:
                # Start of the method
                in_method = True
                brace_count = line.count("{") - line.count("}")  # Track braces in the current line

                # Determine the indentation level of the method
                indentation = len(line) - len(line.lstrip())
                indented_new_content = "\n".join(
                    " " * indentation + new_line for new_line in new_method_content.splitlines()
                )

                # Replace the entire method with the indented new content
                updated_lines.append(indented_new_content + "\n")
            elif in_method:
                # Track braces to find the end of the method
                brace_count += line.count("{") - line.count("}")
                if brace_count == 0:
                    in_method = False  # End of the method
            else:
                updated_lines.append(line)  # Keep lines outside the method

        # Write the updated content back to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(updated_lines)

        print(f"Method '{method_name}' replaced successfully in {file_path}")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def replace_php_section(file_path, start_marker, end_marker, new_content):
    """
    Replace a section of a PHP file between start_marker and end_marker with new_content.

    :param file_path: Path to the PHP file.
    :param start_marker: The marker indicating the start of the section to replace.
    :param end_marker: The marker indicating the end of the section to replace.
    :param new_content: The new content to insert between the markers.
    """
    try:
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Find the section to replace
        in_section = False
        updated_lines = []
        for line in lines:
            if start_marker in line:
                in_section = True
                updated_lines.append(line)  # Keep the start marker
                updated_lines.append(new_content + "\n")  # Add the new content
            elif end_marker in line and in_section:
                in_section = False
                updated_lines.append(line)  # Keep the end marker
            elif not in_section:
                updated_lines.append(line)  # Keep lines outside the section

        # Write the updated content back to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(updated_lines)

        print(f"Section replaced successfully in {file_path}")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
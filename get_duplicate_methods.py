"""
The current script identifies all the duplicate methods 
present in the python scripts of a given folder, and 
includes them into a new python file.
Any python scripts in sub-folders are included as well.

"""

import os
import ast


def get_all_file_names(folder_path: str, file_extension: str) -> list:
    """

    The metod identifies all the file names with a specific
    file extension that are present in a target folder. 

    Args:
        folder_path (str): The path of the target folder
        file_extension(str): file extensions to be taken into 
                            account (i.e. '.py')

    Returns:
        list: All the file names with the target extension
            that are present in the folder

    """
    file_names = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(file_extension):
                file_path = os.path.join(root, file)
                file_names.append(file_path)

    print(str(len(file_names)) + " '" + str(file_extension) +
          "' files are present in this folder")

    return file_names


def extract_function_names(script_path: str) -> list:
    """

    Method identifies all the function names of a given python script,
    and returns them in a list.

    Args:
        script_path (str): The path of the investiageted python script. 

    Returns:
        list: All the methods in the target python script

    """
    with open(script_path, 'r') as file:
        source_code = file.read()

    function_names = []
    parsed_ast = ast.parse(source_code)

    for node in ast.walk(parsed_ast):
        if isinstance(node, ast.FunctionDef):
            function_names.append(node.name)

    return function_names


def find_duplicate_entries(list_dict: dict) -> dict:
    """

    Method reads a dicitionary and identifies 
    all the dicitonary values that correpsond
    to 2 or more dictionary keys.

    Args:
        list_dict (dict): The original dictionary.

    Returns:
        dict: The duplicate entries dictionary.

    """
    all_lists = list_dict.values()
    duplicates = {}

    for lst_name, lst in list_dict.items():
        for entry in lst:
            count = sum(1 for sublist in all_lists if entry in sublist)
            # return only the first script name were the duplicate method is encountered
            if count >= 2:
                if entry not in duplicates:
                    duplicates[entry] = lst_name

    duplicates = {entry: lists for entry,
                  lists in duplicates.items() if len(lists) > 0}
    return duplicates


def extract_duplicate_methods_into_file(file_names: list,
                                        method_names: list,
                                        new_file_name: str):
    """

    The method receives a list of file and method names as its input.
    Every individual method is read from its corresponding python file,
    and added into a new python file.
    The new python file includes all the methods in the method list. 

    Args:
        file_names (list): The files to be accessed.
        method_names (list): The methods to be extracted.
        new_file_name (str): The name of the new file to be created.

    """
    try:
        if not os.path.exists(new_file_name):
            # Create the new file if it doesn't exist
            open(new_file_name, "x").close()

        with open(new_file_name, "a") as new_file:
            for i in range(len(file_names)):
                target_file_name = file_names[i]
                target_method_name = method_names[i]

                with open(target_file_name, "r") as file:
                    file_contents = file.read()

                # Find the start and end indices of the target method
                start_index = file_contents.find("def " + target_method_name)
                if start_index == -1:
                    print(
                        f"Method '{target_method_name}' not found in '{target_file_name}'.")
                    continue

                # Find the end of the method
                end_index = file_contents.find("def ", start_index + 1)
                if end_index == -1:
                    end_index = len(file_contents)
                else:
                    return_index = file_contents.find(
                        "return ", start_index, end_index)
                    if return_index != -1:
                        next_def_index = file_contents.find(
                            "def ", return_index, end_index)
                        if next_def_index != -1:
                            end_index = next_def_index

                # Extract the target method
                extracted_contents = file_contents[start_index:end_index]

                # Write the extracted method to the new file
                new_file.write(extracted_contents)
                new_file.write("\n\n")

        print(f"Methods extracted successfully to '{new_file_name}'.")
    except FileNotFoundError:
        print("File not found.")
    except IOError:
        print("Error reading or writing the file.")


def identify_duplicate_functions(folder_path: str,
                                 file_extension: str,
                                 new_file_name: str) -> dict:
    """

    The method scans the contents of a given folder and identifies
    all the files of a given extension ('.py'). Then identifies
    all the python  methods present in 2 or more scripts ('duplicates')
    and transcribes them into a new python file. 

    Args:
        folder_path (str): The investigated folder name.
        file_extension (str): The file extension taken into account ('.py')
        new_file_name (str): The name of the new file.

    Returns:
        dict: The names of all the duplicate methods and the python files
            they can be found in.

    """
    script_name_paths = get_all_file_names(folder_path, file_extension)

    # instantiate a dictionary, whose keys are the target_script_paths
    target_script_dict = {value: None for value in script_name_paths}

    # assign all the methods to their corresonding script
    for target_script_path in target_script_dict.keys():
        target_script_dict[target_script_path] = extract_function_names(
            target_script_path)

    duplicate_methods_dict = find_duplicate_entries(target_script_dict)
    print(str(len(duplicate_methods_dict)) +
          ' duplicate methods where identified')

    # create a new python file that includes all the duplicate methods
    extract_duplicate_methods_into_file(file_names=list(duplicate_methods_dict.values()),
                                        method_names=list(
                                            duplicate_methods_dict.keys()),
                                        new_file_name=new_file_name)

    return duplicate_methods_dict

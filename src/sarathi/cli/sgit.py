import subprocess

from sarathi.llm.call_llm import call_llm_model
from sarathi.llm.prompts import prompt_dict
from sarathi.utils.formatters import format_green


def get_staged_diff():
    """Returns the staged difference in the git repository.

    Returns:
        The staged difference in the git repository as a string.
    """
    return subprocess.run(
        ["git", "diff", "--staged"], stdout=subprocess.PIPE
    ).stdout.decode("utf-8")


def generate_commit_message():
    """Generates a commit message using a language model.

    Returns:
        The commit message generated by the language model.
    """
    diff = get_staged_diff()
    prompt_info = prompt_dict["autocommit"]
    llm_response = call_llm_model(prompt_info, diff)
    return llm_response["choices"][0]["message"]["content"]


def get_user_confirmation():
    """Prompts the user for confirmation to proceed.

    Returns:
        True if user input is y, False otherwise.
    """
    return input(f"Do you want to proceed " + format_green("y/n") + ": ").strip() == "y"


def setup_args(subparsers, opname):
    """Adds a new sub-parser to the provided subparsers.

    Args:
        subparsers: The argument parser object to which a new sub-parser will be added.
        opname: The name of the sub-parser to be added.

    Returns:
        The newly added sub-parser object.
    """
    git_parser = subparsers.add_parser(opname)
    git_sub_cmd = git_parser.add_subparsers(dest="git_sub_cmd")
    git_sub_cmd.add_parser("autocommit")
    git_sub_cmd.add_parser("gencommit")


def execute_cmd(args):
    """
    Executes a Git sub-command based on the provided arguments.

    Args:
        args: The arguments containing the Git sub-command to be executed.

    Returns:
        None
    """
    if args.git_sub_cmd == "gencommit":
        generated_commit_msg = generate_commit_message()
        if generated_commit_msg:
            subprocess.run(["git", "commit", "-m", generated_commit_msg])
            subprocess.run(["git", "commit", "--amend"])
    elif args.git_sub_cmd == "autocommit":
        generated_commit_msg = generate_commit_message()
        if generated_commit_msg:
            print("**Below is the generated commit messaged **\n")
            print(generated_commit_msg)
            if get_user_confirmation():
                subprocess.run(["git", "commit", "-m", generated_commit_msg])
            else:
                print("I would try to generate a better commit msgs next time")

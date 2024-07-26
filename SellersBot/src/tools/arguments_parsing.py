def remove_all_extra_spaces_for_arguments(string: str) -> str:
    return " ".join(string.split())


def remove_all_spaces(input_str):
    return ''.join(input_str.split())


def get_arguments(message_text: str) -> list[str]:
    return remove_all_extra_spaces_for_arguments(message_text).split(" ")[1:]

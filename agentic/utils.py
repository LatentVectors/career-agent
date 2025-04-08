def print_max_width(text: str, width: int = 80) -> None:
    """Print text with a maximum width."""
    words = text.split(" ")
    current_length = 0
    line = ""
    for word in words:
        word_len = len(word)
        if current_length + word_len + 1 > width:
            print(line)
            line = word + " "
            current_length = word_len + 1
        else:
            line += word + " "
            current_length += word_len + 1
    if len(line) > 0:
        print(line)

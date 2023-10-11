import textwrap


def textwrap_lines(line_str, width=150, indent="  "):
    """ Wrap str to target width with specified indentation while preserving line breaks

    Args:
        line_str (str): str with line breaks that caller wishes to preserve
        width (int): target max width of each line. long words are not broken so line(s) may have width greater than
            this value. Default 150
        indent (str): prepend every line with this str. Default "  "

    Returns:
        str: line_str with line breaks preserved, indentation applied and width target per line approximated
    """
    return '\n'.join(['\n'.join(textwrap.wrap(line, width=width, break_long_words=False, replace_whitespace=False,
                                              initial_indent=indent, subsequent_indent=indent))
                      for line in line_str.splitlines() if line.strip() != ''])
from typing import Optional
import builtins
import colorama
import sys


def console_style(fcolor, bcolor):
    """ Create console specific colorama style string from arguments

    Args:
        fcolor (Optional[str]): foreground color. Default None to use default color
        bcolor (Optional[str]): background color. Default None to use default color

    Returns:
        str: colorama style string
    """
    if fcolor is None:
        fcolor = colorama.Fore.RESET
    elif fcolor == "blue":
        fcolor = colorama.Fore.BLUE
    elif fcolor == "red":
        fcolor = colorama.Fore.RED
    else:
        fcolor = colorama.Fore.RESET

    # most likely bcolor is None so check None first
    if bcolor is None:
        bcolor = colorama.Back.RESET
    else:
        bcolor = colorama.Back.RESET

    return fcolor + bcolor


def print(print_str, end='\n', flush=False, fcolor=None, bcolor=None):  # known special case of print
    """ Console (sys.stdout) specific print function with colorama style options

    Args:
        print_str (str): printed to console. this function does not accept *args for objects to print.
        end (str): specify what to print at the end. Default '\n'.
        flush (boolean): True to flush output. Default False to buffer output.
        fcolor (Optional[str]): foreground color. Default None to use default color
        bcolor (Optional[str]): background color. Default None to use default color
    """
    builtins.print(console_style(fcolor, bcolor) + print_str + colorama.Style.RESET_ALL, end=end, file=sys.stdout,
                   flush=flush)


def input(prompt, fcolor=None, bcolor=None):
    """ Console (sys.stdout) specific input function with colorama style options

    Args:
        prompt (str): printed to console
        fcolor (Optional[str]): foreground color. Default None to use default color
        bcolor (Optional[str]): background color. Default None to use default color

    Returns:
        str: user input
    """
    return builtins.input(console_style(fcolor, bcolor) + prompt + colorama.Style.RESET_ALL)
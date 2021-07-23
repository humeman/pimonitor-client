import textwrap
import time

import apiclient

termcolors = {
    "default": "\033[37m",
    "bold": "\033[1m",
    "reset": "\033[0m",

    "red": "\033[31m",
    "light_red": "\033[91m",

    "green": "\033[32m",
    "light_green": "\033[39m",

    "yellow": "\033[33m",
    "light_yellow": "\033[93m",

    "blue": "\033[34m",
    "light_blue": "\033[94m",

    "magenta": "\033[35m",
    "light_magenta": "\033[95m",

    "cyan": "\033[36m",
    "light_cyan": "\033[96m",

    "light_gray": "\033[37m",
    "dark_gray": "\033[90m"
}

adapters = {
    "warn": "yellow",
    "error": "red",
    "success": "green",
    "start": "cyan",
    "stop": "cyan",
    "close": "cyan",
    "cmd": "blue",
    "int": "blue",
    "info": "default",
    "obj": "magenta",
    "msg": "magenta",
    "api": "blue"
}

def log(
        log_type: str = "",
        message: str = "",
        bold: bool = False,
        color: str = "default",
        condition: bool = True
    ):
        if not condition:
            return

        color = color.lower()

        if color == "default":
            if log_type in adapters:
                color = adapters[log_type]

        try:
            col = termcolors[color]

            if color in ["bold", "reset"]:
                raise apiclient.classes.exceptions.NotFound(f"Color cannot be bold or reset.")

        except:
            raise apiclient.classes.exceptions.NotFound(f"Invalid color {color}.")

        if hasattr(apiclient, "timer"):
            timer = apiclient.timer

        else:
            timer = time.time()

        timelen = 16
        typelen = 8

        timestr = f"[{round(time.time() - timer, 3)}]"
        typestr = f"[{log_type.upper()}]"

        timestr += " " * (timelen - len(timestr))
        typestr += " " * (typelen - len(typestr))

        bold_str = termcolors["bold"] if bold else ""

        print(f"{col}{termcolors['bold']}{timestr}{typestr}\t{termcolors['reset']}{col}{bold_str}{message}{termcolors['reset']}")

def log_step(
        content: str,
        color: str = "default",
        bold: bool = False
    ):
    
    color = termcolors[color]
    bold_col = termcolors["bold"]
    reset = termcolors["reset"]

    for line in [content[i:i+150] for i in range(0, len(content), 150)]:
        print(f"                                {color}{bold_col}→ {reset}{color}{bold_col if bold else ''}{line}{reset}")


def log_long(
        content: str,
        color: str,
        remove_blank_lines: bool = False,
        extra_line: bool = True
    ):
    color = termcolors[color]
    bold = termcolors["bold"]
    reset = termcolors["reset"]

    for line in textwrap.dedent(content).split("\n"):
        if line.strip() == "" and remove_blank_lines:
            continue
        
        print(f"                                {color}{bold}→ {reset}{color}{line}{reset}")
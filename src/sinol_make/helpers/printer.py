import curses

from datetime import datetime, timedelta
from curses import wrapper


def printer(func, *args, **kwargs):
    """
    Prints output of func (called every 0.1 seconds with terminal width and height, then args and kwargs)
    to terminal in less-style.
    :param func: function called to get output. Should return a triple (output, title, footer),
                 where output is a list of lines to print,
                 title is a string printed at the top of the terminal,
                 and footer is a string printed at the bottom of the terminal.
                 Title and footer can be None.
    :param args: args for func
    :param kwargs: kwargs for func
    """
    wrapper(_printer, None, func, *args, **kwargs)


def printer_thread(run_event, func, *args, **kwargs):
    """
    Same as printer, but with threading.Event to stop printing.
    :param run_event: threading.Event that is set when printer should stop
    :param func: function called to get output. Should return a triple (output, title, footer),
                 where output is a list of lines to print,
                 title is a string printed at the top of the terminal,
                 and footer is a string printed at the bottom of the terminal.
                 Title and footer can be None.
    :param args: args for func
    :param kwargs: kwargs for func
    """
    wrapper(_printer, run_event, func, *args, **kwargs)


def _printer(stdscr: curses.window, run_event, func, *args, **kwargs):
    """
    Function called by curses.wrapper to print output of func (called with terminal width and height, then args and kwargs) to terminal in less-style.
    :param func: function called to get output. Should return a triple (output, title, footer),
                 where output is a list of lines to print,
                 title is a string printed at the top of the terminal,
                 and footer is a string printed at the bottom of the terminal.
                 Title and footer can be None.
    :param args: args for func
    :param kwargs: kwargs for func
    """

    curses.start_color()
    curses.curs_set(0)
    stdscr.idcok(False)
    stdscr.idlok(False)
    stdscr.erase()
    stdscr.refresh()
    stdscr.nodelay(True)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)

    curr_row = 0
    last_output = []
    last_title = None
    last_footer = None
    output = ['']
    title = None
    footer = None
    time = datetime.now()
    try:
        while run_event is None or run_event.is_set():
            inpt = stdscr.getch()
            height, width = stdscr.getmaxyx()

            if datetime.now() - time > timedelta(seconds=0.1):
                time = datetime.now()
                output, title, footer = func(width, height, *args, **kwargs)

            visible_height = height
            if title is not None:
                visible_height -= 1
            if footer is not None:
                visible_height -= 1

            row_change = False
            if len(output) > height:
                if inpt != curses.ERR:
                    row_change = True
                    if inpt == curses.KEY_DOWN:
                        curr_row = min(curr_row + 1, len(output) - visible_height)
                    elif inpt == curses.KEY_UP:
                        curr_row = max(curr_row - 1, 0)
                    elif inpt == curses.KEY_NPAGE:
                        curr_row = min(curr_row + visible_height, len(output) - visible_height)
                    elif inpt == curses.KEY_PPAGE:
                        curr_row = max(curr_row - visible_height, 0)
                    elif inpt == curses.KEY_END:
                        curr_row = len(output) - visible_height
                    elif inpt == curses.KEY_HOME:
                        curr_row = 0
                    else:
                        row_change = False

            if last_output[curr_row:curr_row + visible_height] != output[curr_row:curr_row + visible_height] \
                    or row_change or last_title != title or last_footer != footer:
                stdscr.erase()

                if title is not None:
                    stdscr.addnstr(0, 0, title.ljust(width), width, curses.color_pair(5))
                _print_to_scr(stdscr, '\n'.join(output[curr_row:curr_row + visible_height]), title, footer)
                if footer is not None:
                    try:
                        stdscr.addnstr(height - 1, 0, footer.ljust(width), width, curses.color_pair(5))
                    except curses.error:  # Curses raises error when trying to write in the lower right corner, but it can be ignored
                        pass

                stdscr.refresh()
            last_output = output
            last_title = title
            last_footer = footer
    except KeyboardInterrupt:
        return


def _print_to_scr(scr: curses.window, output, title, footer):
    """
    Prints output to scr. Replaces color escape sequences with curses color escape sequences.
    """
    s = ""
    y = 0
    new_y = 0
    if title is not None:
        y = 1
        new_y = 1
    x = 0
    new_x = 0
    color = curses.A_NORMAL
    i = 0
    while i < len(output):
        if output[i] == '\033' and i + 4 < len(output):
            if output[i + 1:i + 5] == '[00m':  # End of color
                scr.addstr(y, x, s, color)
                s = ""
                x = new_x
                y = new_y
                color = curses.A_NORMAL
            else:
                try:
                    scr.addstr(y, x, s, color)
                except curses.error:  # Curses raises error when trying to write in the lower right corner, but it can be ignored
                    pass
                s = ""
                x = new_x
                y = new_y

                if output[i + 1:i + 5] == '[01m':  # Bold
                    color = curses.A_BOLD
                elif output[i + 1:i + 5] == '[91m':  # Red
                    color = curses.color_pair(2)
                elif output[i + 1:i + 5] == '[92m':  # Green
                    color = curses.color_pair(3)
                elif output[i + 1:i + 5] == '[93m':  # Yellow
                    color = curses.color_pair(4)
                else:
                    color = curses.color_pair(1)  # White on black
            i += 4
        else:
            s += output[i]
            if output[i] == '\n':
                new_y += 1
                new_x = 0
            else:
                new_x += 1

        i += 1

    try:
        scr.addstr(y, x, s, color)
    except curses.error:  # Curses raises error when trying to write in the lower right corner, but it can be ignored
        pass

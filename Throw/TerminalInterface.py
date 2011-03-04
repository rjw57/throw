import sys
import logging
import formatter

try:
    import curses
    _has_curses = True
except:
    _has_curses = False

class TerminalInterface(object):
    _instance = None
    _log = logging.getLogger('Throw.TerminalInterface')

    class DumbBackend(object):
        def __init__(self, output_stream):
            self._width = 72
            self._output = output_stream
            self._writer = formatter.DumbWriter(output_stream, maxcol=self._width)

        def message(self, message_str):
            for paragraph in message_str.split('\n\n'):
                self._writer.send_flowing_data(paragraph.strip())
                self._writer.send_paragraph(2)

        def input(self, prompt = '', no_echo = False):
            try:
                import readline
            except ImportError:
                pass

            if no_echo:
                import getpass
                return getpass.getpass(prompt)
            else:
                return input(prompt)

    class CursesBackend(DumbBackend):
        # Some of this class is taken from 
        # http://code.activestate.com/recipes/475116-using-terminfo-for-portable-color-output-cursor-co/
        
        _COLORS = "BLACK BLUE GREEN CYAN RED MAGENTA YELLOW WHITE".split()
        _ANSICOLORS = "BLACK RED GREEN YELLOW BLUE MAGENTA CYAN WHITE".split()

        def __init__(self, output_stream):
            TerminalInterface.DumbBackend.__init__(self, output_stream)

            curses.setupterm(fd = output_stream.fileno())

            # Colors
            self.RESET_FG_BG = curses.tigetstr('op').decode('ascii')

            set_fg = curses.tigetstr('setf').decode('ascii')
            if set_fg:
                for i,color in zip(range(len(self._COLORS)), self._COLORS):
                    setattr(self, str(color), curses.tparm(set_fg, i).decode('ascii') or '')
            set_fg_ansi = curses.tigetstr('setaf').decode('ascii')
            if set_fg_ansi:
                for i,color in zip(range(len(self._ANSICOLORS)), self._ANSICOLORS):
                    setattr(self, color, curses.tparm(set_fg_ansi, i).decode('ascii') or '')
            set_bg = curses.tigetstr('setb').decode('ascii')
            if set_bg:
                for i,color in zip(range(len(self._COLORS)), self._COLORS):
                    setattr(self, 'BG_'+color, curses.tparm(set_bg, i).decode('ascii') or '')
            set_bg_ansi = curses.tigetstr('setab').decode('ascii')
            if set_bg_ansi:
                for i,color in zip(range(len(self._ANSICOLORS)), self._ANSICOLORS):
                    setattr(self, 'BG_'+color, curses.tparm(set_bg_ansi, i).decode('ascii') or '')

        def message(self, message_str):
            # Update the writer with the current terminal width
            self._width = min(curses.tigetnum('cols'), 72)
            self._writer = formatter.DumbWriter(self._output, maxcol=self._width)

            #self._writer.send_literal_data(self.GREEN)
            TerminalInterface.DumbBackend.message(self, message_str)
            #self._writer.send_literal_data(self.RESET_FG_BG)

        def input(self, prompt, *args, **kwargs):
            return TerminalInterface.DumbBackend.input(self,
                self.GREEN + prompt + self.RESET_FG_BG, *args, **kwargs)

    # Implement the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TerminalInterface, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self, stream=sys.stdout):
        # Try to import curses and setup a terminal if our output is a TTY.
        if stream.isatty() and _has_curses:
            self._backend = TerminalInterface.CursesBackend(stream)
        else:
            # By default, use a dumb terminal backend
            self._backend = TerminalInterface.DumbBackend(stream)

    def message(self, message):
        self._backend.message(message)

    def input(self, prompt, *args, **kwargs):
        return self._backend.input(prompt=prompt, *args, **kwargs)


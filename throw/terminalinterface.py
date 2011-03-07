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

        def horiz_rule(self):
            self._writer.send_literal_data('-' * self._width)
            self._writer.send_paragraph(1)

        def literal_message(self, message_str):
            self._writer.send_literal_data(message_str)
            self._writer.send_paragraph(2)

        def message(self, message_str):
            for paragraph in message_str.split('\n\n'):
                self._writer.send_flowing_data(paragraph.strip())
                self._writer.send_paragraph(2)

        def error(self, message_str):
            self.message(message_str)

        def input(self, prompt = '', no_echo = False):
            if no_echo:
                import getpass
                return getpass.getpass(prompt)
            else:
                # This magic is to support Python 3 as well as Python 2.
                try:
                    return raw_input(prompt)
                except NameError:
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
                    setattr(self, color, curses.tparm(set_fg, i).decode('ascii') or '')
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

            TerminalInterface.DumbBackend.message(self, message_str)

        def error(self, message_str):
            # Update the writer with the current terminal width
            self._width = min(curses.tigetnum('cols'), 72)
            self._writer = formatter.DumbWriter(self._output, maxcol=self._width)

            self._writer.send_literal_data(self.RED)
            TerminalInterface.DumbBackend.message(self, message_str)
            self._writer.send_literal_data(self.RESET_FG_BG)

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
            try:
                self._backend = TerminalInterface.CursesBackend(stream)
            except curses.error:
                self._backend = TerminalInterface.DumbBackend(stream)
        else:
            # By default, use a dumb terminal backend
            self._backend = TerminalInterface.DumbBackend(stream)

    def input_fields(self, preamble, *args):
        """Get a set of fields from the user. Optionally a preamble may be
        shown to the user secribing the fields to return. The fields are
        specified as the remaining arguments with each field being a a
        list with the following entries:

            - a programmer-visible name for the field
            - a string prompt to show to the user
            - one of the following values:
                - string: return a string from the user
                - password: return a string from the user but do not echo the
                  input to the screen
                - boolean: return a boolean value from the user
                - integer: return an integer value from the user
            - the default value (optional)

        Fields are requested from the user in the order specified.

        Fields are returned in a dictionary with the field names being the keys
        and the values being the items.

        """

        self.new_section()
        if preamble is not None:
            self.message(preamble)

        if any([True for x in args if len(x) > 3]):
            self.message("""
                Some questions have default answers which can be selected by
                pressing 'Enter' at the prompt.""")

        output_dict = { }
        for field in args:
            (field_name, prompt, field_type) = field[:3]

            default = None
            if len(field) > 3:
                default = field[3]

            if field_type == 'string':
                output_dict[field_name] = self.input(prompt, default = default)
            elif field_type == 'password':
                output_dict[field_name] = self.input(prompt, no_echo=True)
            elif field_type == 'boolean':
                output_dict[field_name] = self.input_boolean(prompt, default = default)
            elif field_type == 'integer':
                output_dict[field_name] = self.input_integer(prompt, default = default)

        return output_dict

    def new_section(self):
        self._backend.horiz_rule()

    def message(self, message):
        self._backend.message(message)

    def error(self, message):
        self._backend.error(message)

    def literal_message(self, message):
        self._backend.literal_message(message)

    def input(self, prompt, default = None, *args, **kwargs):
        def_str = ''
        if default is not None:
            def_str = ' [%s]' % (default,)
        input_val = self._backend.input(prompt=prompt + def_str + ': ', *args, **kwargs)
        if default is not None and input_val == '':
            return default
        return input_val

    def input_integer(self, prompt, default = None):
        def_str = None
        if default is not None:
            def_str = str(default)
        while True:
            try:
                input_val = self.input(prompt, default = def_str)
                return int(input_val)
            except ValueError:
                pass

            self.error('I expected a number, try again.')

    def input_boolean(self, prompt, default = None):
        def_str = None
        if default is not None:
            if default:
                def_str = 'YES'
            else:
                def_str = 'NO'
        while True:
            input_val = self.input(prompt + ' (YES/NO)', default = def_str)

            if default is not None and input_val == '':
                return default

            if len(input_val) > 0:
                if input_val[0] == 'y' or input_val[0] == 'Y':
                    return True
                elif input_val[0] == 'n' or input_val[0] == 'N':
                    return False
            
            self.message("I'm afraid I didn't understand that: please type 'YES' or 'NO'.")

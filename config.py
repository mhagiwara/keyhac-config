
import time
from time import strftime
import threading


class KeyLogger(object):

    LOG_FILENAME = '/Users/masato/keys.log'
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
    TIMESTAMP_INTERVAL = 10

    def __init__(self):
        self.log_file = open(self.LOG_FILENAME, mode='a')
        # list of letters to log.
        self.buffer = []

        def timer_func():
            """A thread function which periodically writes out the current timestamp."""
            while True:
                self.write_to_file()
                time.sleep(self.TIMESTAMP_INTERVAL)

        # Start the timer thread
        timer_thread = threading.Thread(target=timer_func)
        timer_thread.start()

    def log_single_letter(self, letter):
        self.buffer.append(letter)

    def write_to_file(self):
        self.log_file.write(strftime(self.TIMESTAMP_FORMAT) + '\t')
        self.log_file.write(' '.join(self.buffer) + '\n')
        self.log_file.flush()
        self.buffer = []


def configure(keymap):
    """Main entry point for keyhac customization."""

    key_logger = KeyLogger()

    gkeymap = keymap.defineWindowKeymap()

    def key_down_letter(key, letter_to_log):
        """Helper function to handle lower-cased letters and others."""
        key_logger.log_single_letter(letter_to_log)
        keymap.InputKeyCommand(key)()

    key_letter_map = [
        ('Space', 'Space'),
        ('Tab', 'Tab'),
        ('Back', 'Back'),
        ('Enter', 'Enter'),

        ('BackQuote', '`'),
        ('Minus', '-'),
        ('Plus', '='),
        ('OpenBracket', '['),
        ('CloseBracket', ']'),
        ('BackSlash', '\\'),
        ('Colon', ';'),
        ('Quote', '\''),
        ('Comma', ','),
        ('Period', '.'),
        ('Slash', '/'),

        ('Shift-BackQuote', '~'),
        ('Shift-1', '!'),
        ('Shift-2', '@'),
        ('Shift-3', '#'),
        ('Shift-4', '$'),
        ('Shift-5', '%'),
        ('Shift-6', '^'),
        ('Shift-7', '&'),
        ('Shift-8', '*'),
        ('Shift-9', '('),
        ('Shift-0', ')'),
        ('Shift-Minus', '_'),
        ('Shift-Plus', '+'),
        ('Shift-OpenBracket', '{'),
        ('Shift-CloseBracket', '}'),
        ('Shift-BackSlash', '|'),
        ('Shift-Colon', ':'),
        ('Shift-Quote', '"'),
        ('Shift-Comma', '<'),
        ('Shift-Period', '>'),
        ('Shift-Slash', '?')
    ]
    key_letter_map.extend([(ch, ch) for ch in 'abcdefghijklmnopqrstuvwxyz0123456789'])
    key_letter_map.extend([('Shift-'+ch, ch.upper()) for ch in 'abcdefghijklmnopqrstuvwxyz'])

    for key, letter in key_letter_map:
        gkeymap[key] = lambda key=key, letter=letter: key_down_letter(key, letter)

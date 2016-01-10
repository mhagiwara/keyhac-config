
import time
from datetime import datetime as dt
from datetime import timedelta as td
import threading
import zlib

LOG_FILENAME = '/Users/masato/keys.log'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
REPORT_FILENAME = '/Users/masato/keys.html'
REPORT_DATE_FORMAT = '%Y-%m-%d'


class KeyLogger(object):

    TIMESTAMP_INTERVAL = 10

    def __init__(self):
        self.log_file = open(LOG_FILENAME, mode='a')
        # list of letters to log.
        self.buffer = []
        self.stopped = False

        def timer_func():
            """A thread function which periodically writes out the current timestamp."""
            while not self.stopped:
                self.write_to_file()
                time.sleep(self.TIMESTAMP_INTERVAL)

        # Start the timer thread
        timer_thread = threading.Thread(target=timer_func)
        timer_thread.start()

    def log_single_letter(self, letter):
        self.buffer.append(letter)

    def write_to_file(self):
        self.log_file.write(dt.now().strftime(TIMESTAMP_FORMAT) + '\t')
        self.log_file.write(' '.join(self.buffer) + '\n')
        self.log_file.flush()
        self.buffer = []

        r = Report(LOG_FILENAME)
        r.write()

    def stop(self):
        self.stopped = True


class Report(object):
    def __init__(self, log_filename):
        self.stats = self.read_stats(log_filename)

    def write(self):
        # report_file = open(REPORT_FILENAME, mode='w')
        print('<report>')
        today = dt.now()
        for d in range(7, -1, -1):
            d_days_ago = today + td(days=-d)
            timestamp = d_days_ago.strftime(REPORT_DATE_FORMAT)
            keys = self.stats.get(d_days_ago.strftime(REPORT_DATE_FORMAT), [])
            key_joined = ' '.join(keys)
            key_compressed = zlib.compress(bytes(key_joined, 'UTF-8'))

            print('%s keys=%s, str_len=%s, compressed=%s'
                  % (timestamp, len(keys), len(key_joined), len(key_compressed)))
        print('</report>')

    def read_stats(self, filename):
        """Returns a dict from timestamp (REPORT_DATE_FORMAT) to list of all keys on that day."""
        log_file = open(filename)
        day_keys = {}
        for line in log_file:
            fields = line.strip().split('\t')
            if len(fields) == 2:
                timestamp, keys_str = fields
                logged_time = dt.strptime(timestamp, TIMESTAMP_FORMAT)
                keys = keys_str.split(' ')
                day_keys.setdefault(logged_time.strftime(REPORT_DATE_FORMAT), []).extend(keys)
        return day_keys


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

    gkeymap['Fn-5'] = lambda: key_logger.stop()

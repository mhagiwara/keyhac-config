
import time
from datetime import datetime as dt
from datetime import timedelta as td
import threading
import zlib
import json
from collections import defaultdict


LOG_FILENAME = '/Users/masato/keys.log'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
REPORT_TEMPLATE_FILENAME = '/Users/masato/Library/Application Support/Keyhac/report.html'
REPORT_FILENAME = '/Users/masato/keys.html'
REPORT_DATE_FORMAT = '%Y-%m-%d'


def calc_moppol(keys):
    """Given a list of pressed keys, returns the value of moppol (the unit of amount worked)."""
    key_joined = ' '.join(keys)
    key_compressed = zlib.compress(bytes(key_joined, 'UTF-8'))
    return len(key_compressed) - 8      # subtract 8 because compressed empty string has len=8


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
        # Create the data for heatmap.
        data = []
        per_day_keys = defaultdict(list)
        today = dt.now()
        for d in range(6, -1, -1):  # from 6 days ago to today (0 days ago).
            d_days_ago = today + td(days=-d)
            timestamp = d_days_ago.strftime(REPORT_DATE_FORMAT)
            day = d_days_ago.isoweekday()
            per_hour_keys = self.stats.get(timestamp, {})

            for hour in range(0, 24):  # from 0 to 23
                keys = per_hour_keys.get(hour, [])
                moppol = calc_moppol(keys)
                data.append({'day': day,
                             'hour': hour+1,
                             'value': moppol})
                per_day_keys[day].extend(keys)

        # Read the template & replace the placeholder
        with open(REPORT_TEMPLATE_FILENAME, mode='r') as f:
            report_template = f.read()
            report_template = report_template.replace('%DATA%', json.dumps(data))

            # Replace the total placeholder.
            totals_arr = [calc_moppol(per_day_keys[d]) for d in range(1, 8)]
            report_template = report_template.replace('%TOTALS%', json.dumps(totals_arr))

        # Write to file.
        with open(REPORT_FILENAME, mode='w') as f:
            f.write(report_template)

    def read_stats(self, filename):
        """Returns a dict from timestamp (REPORT_DATE_FORMAT)
           to dict from hour (integer from 0 to 23) to list of all keys on that time period."""
        day_hour_keys = defaultdict(lambda: defaultdict(list))

        with open(filename, mode='r') as log_file:
            for line in log_file:
                fields = line.strip().split('\t')
                if len(fields) == 2:
                    timestamp, keys_str = fields
                    logged_time = dt.strptime(timestamp, TIMESTAMP_FORMAT)
                    keys = keys_str.split(' ')
                    date_str = logged_time.strftime(REPORT_DATE_FORMAT)
                    day_hour_keys[date_str][logged_time.hour].extend(keys)
        return day_hour_keys


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

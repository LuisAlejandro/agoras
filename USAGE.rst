Using the application
---------------------

agoras publish
~~~~~~~~~~~~~

This command generates a JSON module index with information from PyPI. Read
below for more information on how to use it::

    $ agoras pypi --help

    usage: agoras pypi [options]

    General Options:
      -V, --version         Print version and exit.
      -h, --help            Show this help message and exit.

    Pypi Options:
      -l <level>, --loglevel <level>
                            Logger verbosity level (default: INFO). Must be one
                            of: DEBUG, INFO, WARNING, ERROR or CRITICAL.
      -f <path>, --logfile <path>
                            A path pointing to a file to be used to store logs.
      -o <path>, --outputfile <path>
                            A path pointing to a file that will be used to store
                            the JSON Module Index (required).
      -R <letter/number>, --letter-range <letter/number>
                            An expression representing an alphanumeric range to be
                            used to filter packages from PyPI (default: 0-z). You
                            can use a single alphanumeric character like "0" to
                            process only packages beginning with "0". You can use
                            commas use as a list o dashes to use as an interval.
      -L <size>, --limit-log-size <size>
                            Stop processing if log size exceeds <size> (default:
                            3M).
      -M <size>, --limit-mem <size>
                            Stop processing if process memory exceeds <size>
                            (default: 2G).
      -T <sec>, --limit-time <sec>
                            Stop processing if process time exceeds <sec>
                            (default: 2100).

import getopt, sys
from core.test import test_core


# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

options = "hc:"
long_options = ["help", "core"]


try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)
    for arg, value in arguments:
        if arg in ('-c', '--core'):
            test_core(value)

except getopt.error as err:
    # output error, and return with an error code
    print (str(err))
import getopt
import sys

# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

options = "hc:p"
long_options = ["help", "core", "pre_processor"]

try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)
    for arg, value in arguments:
        if arg in ('-c', '--core'):
            from core.test import test_core
            test_core(value)
        if arg in ('-p', '--pre_processor'):
            from core.test import pre_processor
            pre_processor()

except getopt.error as err:
    # output error, and return with an error code
    print(str(err))

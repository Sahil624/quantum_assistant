import os

cmd = """voila --no-browser --tornado_settings headers='{"headers": {"Content-Security-Policy": "frame-ancestors 'self' localhost:*"}}'"""

os.system(cmd)
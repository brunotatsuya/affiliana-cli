import sys
from procedures import run_with_docker

# if an arg in sys.argv[1:] has spaces, surround it with quotes
args = [f'"{arg}"' if " " in arg else arg for arg in sys.argv[1:]]

run_with_docker("poetry run python main.py " + " ".join(args))

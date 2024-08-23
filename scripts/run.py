import sys
from scripts.procedures import run_with_docker

command = "poetry run python main.py " + " ".join(sys.argv[1:])

run_with_docker(command)

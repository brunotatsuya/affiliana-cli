import sys
from procedures import run_with_docker

run_with_docker("poetry run python main.py " + " ".join(sys.argv[1:]))

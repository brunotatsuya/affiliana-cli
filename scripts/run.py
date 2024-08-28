import sys
from procedures import run_with_docker

# if an arg in sys.argv[1:] has spaces, surround it with quotes
stop_containers_after = "--stop-containers-after" in sys.argv
args = [f'"{arg}"' if " " in arg else arg for arg in sys.argv[1:]]
if stop_containers_after:
    args.remove("--stop-containers-after")

run_with_docker(
    "poetry run python main.py " + " ".join(args),
    stop_containers_after=stop_containers_after,
)

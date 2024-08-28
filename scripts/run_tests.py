import sys
from procedures import run_with_docker

run_with_docker(
    "poetry run pytest --verbose --cov=. --ignore=docker",
    stop_containers_after="--stop-containers-after" in sys.argv,
    testing=True,
)

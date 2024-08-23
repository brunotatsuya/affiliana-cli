from scripts.procedures import run_with_docker

run_with_docker("poetry run pytest --verbose --cov=. --ignore=docker", testing=True)

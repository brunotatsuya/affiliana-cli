from procedures import run_with_docker

run_with_docker("poetry run alembic -c database/alembic.ini upgrade head")
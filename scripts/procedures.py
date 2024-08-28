import subprocess
import shlex
import time

from typing import Optional

def run_with_docker(command: str, testing: Optional[bool] = False):
    docker_compose_file = (
        "docker/docker-compose.yml" if not testing else "docker/docker-compose.test.yml"
    )
    docker_container_psql_name = (
        "market-research_database" if not testing else "market-research-test_database"
    )

    dc_up = f"docker compose -f {docker_compose_file} up -d --quiet-pull".split(" ")
    dc_isready = f"docker exec {docker_container_psql_name} pg_isready".split(" ")
    dc_down = f"docker compose -f {docker_compose_file} stop".split(" ")

    command = shlex.split(command)

    try:
        subprocess.check_call(dc_up)
        while True:
            try:
                subprocess.check_call(dc_isready)
                break
            except:
                time.sleep(1)
        subprocess.check_call(command)
    finally:
        subprocess.check_call(dc_down)

import subprocess
import shlex
import time

from typing import Optional

def run_with_docker(command: str, testing: Optional[bool] = False):
    service_name = "database" if not testing else "database-test"
    docker_container_psql_name = f"affiliana-cli_{service_name}"

    dc_up = f"docker compose -f docker/docker-compose.yml up -d {service_name} --quiet-pull".split(" ")
    dc_isready = f"docker exec {docker_container_psql_name} pg_isready".split(" ")
    dc_down = f"docker compose -f docker/docker-compose.yml stop".split(" ")

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

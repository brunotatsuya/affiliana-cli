import subprocess
import shlex
import time

from typing import Optional


def run_with_docker(
    command: str,
    stop_containers_after: Optional[bool] = False,
    testing: Optional[bool] = False,
):
    """
    Setups docker containers before running a command and
    optionally stops the containers after the command is executed.

    Args:
        command (str): The command to be executed.
        stop_containers_after (bool, optional): Whether to stop the Docker containers after executing the command. Defaults to False.
        testing (bool, optional): Whether to use the testing Docker compose file. Defaults to False.
    """
    docker_compose_file = (
        "docker/docker-compose.yml" if not testing else "docker/docker-compose.test.yml"
    )
    docker_container_psql_name = (
        "affiliana-cli_database" if not testing else "affiliana-cli-test_database"
    )

    dc_up = f"docker compose -f {docker_compose_file} up -d --quiet-pull".split(" ")
    dc_isready = f"docker exec {docker_container_psql_name} pg_isready".split(" ")
    dc_down = f"docker compose -f {docker_compose_file} stop".split(" ")

    command = shlex.split(command)

    try:
        subprocess.check_call(dc_up)
        while True:
            try:
                subprocess.check_call(dc_isready, stdout=subprocess.DEVNULL)
                break
            except:
                time.sleep(1)
        subprocess.check_call(command)
    finally:
        if stop_containers_after:
            subprocess.check_call(dc_down)

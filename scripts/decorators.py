import subprocess
import time

from typing import Optional


def with_docker(testing: Optional[bool] = False):
    docker_compose_file = (
        "docker/docker-compose.yml" if not testing else "docker/docker-compose.test.yml"
    )
    docker_container_psql_name = (
        "market-research_database" if not testing else "market-research-test_database"
    )
    dc_up = f"docker compose -f {docker_compose_file} up -d --quiet-pull"
    dc_isready = f"docker exec {docker_container_psql_name} pg_isready"
    dc_down = f"docker compose -f {docker_compose_file} stop"

    def wrapper(target_function):
        def decorated_function():
            try:
                subprocess.check_call(dc_up.split(" "))
                while True:
                    try:
                        subprocess.check_call(dc_isready.split(" "))
                        break
                    except:
                        time.sleep(1)
                target_function()
            finally:
                subprocess.check_call(dc_down.split(" "))

        return decorated_function

    return wrapper

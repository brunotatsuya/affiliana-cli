import subprocess
import time

docker_compose_up = (
    "docker compose -f docker/docker-compose.test.yml up -d --quiet-pull"
)
docker_pg_isready = "docker exec market-research-test_database pg_isready"
run_tests = "poetry run pytest  --verbose --cov=."
docker_compose_stop = "docker compose -f docker/docker-compose.test.yml stop"


def build_command(command):
    return command.split(" ")


try:
    subprocess.check_call(build_command(docker_compose_up))
    while True:
        try:
            subprocess.check_call(build_command(docker_pg_isready))
            break
        except:
            time.sleep(1)
    subprocess.check_call(build_command(run_tests))
finally:
    subprocess.check_call(build_command(docker_compose_stop))

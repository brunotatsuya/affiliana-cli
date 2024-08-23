import subprocess

from decorators import with_docker


@with_docker(testing=True)
def run_tests():
    subprocess.check_call(
        "poetry run pytest  --verbose --cov=. --ignore=docker".split(" ")
    )

if __name__ == "__main__":
    run_tests()
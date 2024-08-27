from unittest.mock import Mock, call, patch
import pytest

from scripts.procedures import run_with_docker


@pytest.fixture(autouse=True)
def mock_time_sleep():
    with patch("time.sleep") as mock_time_sleep:
        yield mock_time_sleep


@pytest.fixture
def mock_subprocess_check_call():
    with patch("subprocess.check_call") as mock_subprocess_check_call:
        yield mock_subprocess_check_call


@pytest.mark.parametrize(
    "testing, expected_docker_file, expected_docker_container_name",
    [
        (True, "docker/docker-compose.test.yml", "market-research-test_database"),
        (False, "docker/docker-compose.yml", "market-research_database"),
    ],
)
def test_should_use_correct_docker_file_and_docker_container_name_given_testing_flag(
    testing: bool,
    expected_docker_file: str,
    expected_docker_container_name: str,
    mock_subprocess_check_call: Mock,
):
    run_with_docker("echo hello", testing=testing)
    mock_subprocess_check_call.assert_any_call(
        f"docker compose -f {expected_docker_file} up -d --quiet-pull".split(" ")
    )
    mock_subprocess_check_call.assert_any_call(
        f"docker exec {expected_docker_container_name} pg_isready".split(" ")
    )


def test_should_run_docker_up_at_first_place(mock_subprocess_check_call: Mock):
    run_with_docker("echo hello")
    assert mock_subprocess_check_call.call_args_list[0] == call(
        "docker compose -f docker/docker-compose.yml up -d --quiet-pull".split(" ")
    )


def test_should_call_pg_isready_until_dockerized_postgres_is_ready(
    mock_subprocess_check_call: Mock,
):
    mock_subprocess_check_call.side_effect = [
        None,  # docker compose up
        Exception(),  # pg_isready = false
        Exception(),  # pg_isready = false
        Exception(),  # pg_isready = false
        Exception(),  # pg_isready = false
        None,  # pg_isready = true
        None,  # echo hello
        None,  # docker compose down
    ]

    run_with_docker("echo hello")

    pg_isready_command_args = "docker exec market-research_database pg_isready".split(
        " "
    )

    assert mock_subprocess_check_call.call_args_list[1] == call(pg_isready_command_args)
    assert mock_subprocess_check_call.call_args_list[2] == call(pg_isready_command_args)
    assert mock_subprocess_check_call.call_args_list[3] == call(pg_isready_command_args)
    assert mock_subprocess_check_call.call_args_list[4] == call(pg_isready_command_args)
    assert mock_subprocess_check_call.call_args_list[5] == call(pg_isready_command_args)
    assert mock_subprocess_check_call.call_args_list[6] != call(pg_isready_command_args)


def test_should_wait_1_second_between_pg_isready_calls(
    mock_subprocess_check_call: Mock, mock_time_sleep: Mock
):
    mock_subprocess_check_call.side_effect = [
        None,  # docker compose up
        Exception(),  # pg_isready = false
        Exception(),  # pg_isready = false
        Exception(),  # pg_isready = false
        Exception(),  # pg_isready = false
        None,  # pg_isready = true
        None,  # echo hello
        None,  # docker compose down
    ]

    run_with_docker("echo hello")
    assert mock_time_sleep.call_args_list == [call(1), call(1), call(1), call(1)]


def test_should_run_the_command_after_dockerized_postgres_is_ready(
    mock_subprocess_check_call: Mock,
):
    mock_subprocess_check_call.side_effect = [
        None,  # docker compose up
        Exception(),  # pg_isready = false
        None,  # pg_isready = true
        None,  # echo hello
        None,  # docker compose down
    ]

    run_with_docker("echo hello")
    assert mock_subprocess_check_call.call_args_list[3] == call("echo hello".split(" "))


def test_should_run_docker_compose_down_after_command_is_executed(
    mock_subprocess_check_call: Mock,
):
    run_with_docker("echo hello")
    assert mock_subprocess_check_call.call_args_list[-1] == call(
        "docker compose -f docker/docker-compose.yml stop".split(" ")
    )


def test_should_run_docker_compose_down_even_if_command_fails(
    mock_subprocess_check_call: Mock,
):
    mock_subprocess_check_call.side_effect = [
        None,  # docker compose up
        Exception(),  # pg_isready = false
        None,  # pg_isready = true
        Exception(),  # echo hello
        None,  # docker compose down
    ]

    with pytest.raises(Exception):
        run_with_docker("echo hello")

    assert mock_subprocess_check_call.call_args_list[-1] == call(
        "docker compose -f docker/docker-compose.yml stop".split(" ")
    )

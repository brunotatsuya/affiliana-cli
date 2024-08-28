from app.domain.utils import format_niche_name


def test_should_format_name_correctly():
    assert format_niche_name("Test Niche") == "test niche"

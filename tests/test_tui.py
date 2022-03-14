from weather_command._tui import _generate_title


def test_generate_title_am_pm(mock_location):
    result = _generate_title(mock_location, True)

    assert mock_location.display_name in result
    assert "am" or "pm" in result


def test_generate_title_24_hour(mock_location):
    result = _generate_title(mock_location, False)

    assert mock_location.display_name in result
    assert "am" and "pm" not in result

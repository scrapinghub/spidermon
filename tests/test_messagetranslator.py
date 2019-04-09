import pytest

from spidermon.contrib.validation.translator import MessageTranslator


@pytest.fixture
def message_translator():
    class FixtureMessageTranslator(MessageTranslator):
        messages = {
            r"Simple Message": "Translated Simple Message",
            r"^.+ is a required property$": "Missing Required Property",
            r"Options: (?P<options>.*)": "Translated With Options: {options}",
        }

    return FixtureMessageTranslator()


@pytest.mark.parametrize(
    "original_message,translated_message",
    [
        ("Simple Message", "Translated Simple Message"),
        ("email is a required property", "Missing Required Property"),
        ("Options: a, b, c", "Translated With Options: a, b, c"),
    ],
)
def test_message_translator(message_translator, original_message, translated_message):
    assert message_translator.translate_message(original_message) == translated_message

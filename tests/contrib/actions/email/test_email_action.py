import pytest

from spidermon.contrib.actions.email import SendEmail
from spidermon.exceptions import NotConfigured

SENDER = "sender@example.com"
RECIPIENT = "recipient@example.com"
SUBJECT = "Subject"
MESSAGE = "Message"
BODY_TEXT = "Body Text"


@pytest.fixture
def email(mocker):
    email = SendEmail(
        sender=SENDER, to=RECIPIENT, fake=True, subject=SUBJECT, body_text=BODY_TEXT,
    )
    email.send_message = mocker.MagicMock()
    mocked_message = mocker.MagicMock()
    mocked_message.as_string = mocker.MagicMock()
    email.get_message = mocker.MagicMock(return_value=mocked_message)
    email.render_text_template = mocker.MagicMock()
    email.render_template = mocker.MagicMock()
    return email


@pytest.mark.parametrize(
    "sender,recipient,fake,subject,exception_message",
    [
        (
            None,
            None,
            None,
            None,
            "You must provide at least one recipient for the message.",
        ),
        (SENDER, RECIPIENT, None, None, "You must provide a subject for the message."),
        (
            SENDER,
            None,
            None,
            None,
            "You must provide at least one recipient for the message.",
        ),
    ],
)
def test_init_with_invalid_params(sender, recipient, fake, subject, exception_message):
    with pytest.raises(NotConfigured) as e:
        SendEmail(sender=sender, to=recipient, fake=fake, subject=subject)
    assert exception_message in str(e.value)


def test_run_action_with_fake_present(mocker, email):
    logger = mocker.patch("spidermon.contrib.actions.email.logger")
    email.run_action()
    email.get_message.assert_called_once_with()
    logger.info.assert_called_once_with(email.get_message().as_string())
    email.send_message.assert_not_called()


def test_run_action_without_fake_present(mocker, email):
    logger = mocker.patch("spidermon.contrib.actions.email.logger")
    email.fake = False
    email.run_action()
    email.get_message.assert_called_once_with()
    logger.info.assert_not_called()
    email.send_message.assert_called_once_with(email.get_message())


def test_get_subject_with_subject_present(mocker):
    email = SendEmail(to=RECIPIENT, sender=SENDER, subject=SUBJECT)
    email.result = mocker.MagicMock()
    assert email.get_subject() == SUBJECT


def test_get_subject_without_subject_present(email):
    email.subject = None
    email.subject_template = None
    assert email.get_subject() == ""


def test_get_body_text_with_body_text_present(mocker):
    email = SendEmail(to=RECIPIENT, sender=SENDER, subject=SUBJECT, body_text=BODY_TEXT)
    email.result = mocker.MagicMock()
    assert email.get_body_text() == BODY_TEXT


def test_get_body_text_with_body_text_template_present(mocker):
    email = SendEmail(
        to=RECIPIENT,
        sender=SENDER,
        subject=SUBJECT,
        body_text_template="reports/email/monitors/result.jinja",
    )
    email.result = mocker.MagicMock()
    email.data = mocker.MagicMock()
    assert "<h1>Report Title</h1>" in email.get_body_text()


def test_get_body_text_without_body_present(email):
    email.body_text = None
    email.body_text_template = None
    assert email.get_body_text() == ""

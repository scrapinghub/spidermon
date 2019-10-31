try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call
import pytest

from spidermon.contrib.actions.email import SendEmail
from spidermon.exceptions import NotConfigured

SENDER = "sender@example.com"
RECIPIENT = "recipient@example.com"
SUBJECT = "Subject"
MESSAGE = "Message"
BODY_TEXT = "Body Text"
BODY_HTML = "Body HTML"


@pytest.fixture
def email():
    email = SendEmail(
        sender=SENDER,
        to=RECIPIENT,
        fake=True,
        subject=SUBJECT,
        body_text=BODY_TEXT,
        body_html=BODY_HTML,
    )
    email.send_message = MagicMock()
    mocked_message = MagicMock()
    mocked_message.as_string = MagicMock()
    email.get_message = MagicMock(return_value=mocked_message)
    email.render_text_template = MagicMock()
    email.render_template = MagicMock()
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
    ],
)
def test_init_with_invalid_params(sender, recipient, fake, subject, exception_message):
    with pytest.raises(NotConfigured) as e:
        SendEmail(sender=sender, to=recipient, fake=fake, subject=subject)
    assert exception_message in str(e.value)


def test_init_with_valid_params():
    SendEmail(sender=None, to=None, fake=True, subject=SUBJECT)
    SendEmail(sender=None, to=RECIPIENT, fake=False, subject=SUBJECT)
    SendEmail(sender=SENDER, to=RECIPIENT, fake=False, subject=SUBJECT)


@patch("spidermon.contrib.actions.email.logger")
def test_run_action_with_fake_present(logger, email):
    email.run_action()
    email.get_message.assert_called_once()
    logger.info.assert_called_once_with(email.get_message().as_string())
    email.send_message.assert_not_called()


@patch("spidermon.contrib.actions.email.logger")
def test_run_action_without_fake_present(logger, email):
    email.fake = False
    email.run_action()
    email.get_message.assert_called_once()
    logger.info.assert_not_called()
    email.send_message.assert_called_once_with(email.get_message())


def test_get_subject_with_subject_present(email):
    email.get_subject()
    email.render_text_template.assert_called_once_with(SUBJECT)


def test_get_subject_with_subject_template_present(email):
    email.subject = None
    email.subject_template = "Subject Template"
    email.get_subject()
    email.render_template.assert_called_once_with(email.subject_template)


def test_get_subject_without_subject_present(email):
    email.subject = None
    email.subject_template = None
    subject = email.get_subject()
    assert subject == ""


def test_get_body_text_with_body_text_present(email):
    email.get_body_text()
    email.render_text_template.assert_called_once_with(BODY_TEXT)


def test_get_body_text_with_body_text_template_present(email):
    email.body_text = None
    email.body_text_template = "Body Text Template"
    email.get_body_text()
    email.render_template.assert_called_once_with(email.body_text_template)


def test_get_body_text_without_body_present(email):
    email.body_text = None
    email.body_text_template = None
    body_text = email.get_body_text()
    assert body_text == ""


@patch("spidermon.contrib.actions.email.transform")
def test_get_body_html_with_body_html_present(transform, email):
    email.get_body_html()
    transform.assert_called_once_with(email.render_text_template(email.body_html))


@patch("spidermon.contrib.actions.email.transform")
def test_get_body_html_with_body_html_template_present(transform, email):
    email.body_html = None
    email.body_html_template = "Body HTML Template"
    email.get_body_html()
    transform.assert_called_once_with(email.render_template(email.body_html_template))


@patch("spidermon.contrib.actions.email.transform")
def test_get_body_html_without_body_html_present(transform, email):
    email.body_html = None
    email.body_html_template = None
    body_html = email.get_body_html()
    transform.assert_not_called()
    assert body_html == ""


@pytest.mark.parametrize(
    "recipients, expected_return",
    [
        (RECIPIENT, RECIPIENT),
        ([RECIPIENT, RECIPIENT], "{}, {}".format(RECIPIENT, RECIPIENT)),
        ((RECIPIENT, RECIPIENT), "{}, {}".format(RECIPIENT, RECIPIENT)),
    ],
)
def test_format_recipients(recipients, expected_return):
    email = SendEmail(sender=SENDER, to=RECIPIENT, subject=SUBJECT)
    assert email._format_recipients(recipients) == expected_return


@patch("spidermon.contrib.actions.email.MIMEText")
def test_get_message_without_body_html_cc_bcc_reply_to(MIMEText):
    email = SendEmail(sender=SENDER, to=RECIPIENT, subject=SUBJECT)
    email.get_subject = MagicMock(return_value=SUBJECT)
    email.get_body_text = MagicMock(return_value=BODY_TEXT)
    email.get_body_html = MagicMock(return_value="")
    message = email.get_message()
    email.get_subject.assert_called_once()
    email.get_body_text.assert_called_once()
    email.get_body_html.assert_called_once()

    assert message["Subject"] == SUBJECT
    assert message["From"] == SENDER
    assert message["To"] == RECIPIENT
    assert "Cc" not in message
    assert "Bcc" not in message
    assert "reply-to" not in message
    MIMEText.assert_called_once_with(BODY_TEXT, "plain")


@patch("spidermon.contrib.actions.email.MIMEText")
def test_get_message_with_body_html_cc_bcc_reply_to(MIMEText):
    email = SendEmail(
        sender=SENDER,
        to=RECIPIENT,
        subject=SUBJECT,
        cc=SENDER,
        bcc=SENDER,
        reply_to=SENDER,
    )
    email.get_subject = MagicMock(return_value=SUBJECT)
    email.get_body_text = MagicMock(return_value=BODY_TEXT)
    email.get_body_html = MagicMock(return_value=BODY_HTML)
    message = email.get_message()
    email.get_subject.assert_called_once()
    email.get_body_text.assert_called_once()
    email.get_body_html.assert_called_once()

    assert message["Subject"] == SUBJECT
    assert message["From"] == SENDER
    assert message["To"] == RECIPIENT
    assert message["Cc"] == SENDER
    assert message["Bcc"] == SENDER
    assert message["reply-to"] == SENDER
    MIMEText.assert_has_calls([call(BODY_TEXT, "plain"), call(BODY_HTML, "html")])

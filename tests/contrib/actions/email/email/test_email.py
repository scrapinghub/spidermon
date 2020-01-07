import pytest
from scrapy.utils.test import get_crawler

from spidermon.contrib.actions.email import SendEmail


@pytest.fixture
def mock_render_template(mocker):
    """Mock functions that render templates to return the raw value"""
    mocker.patch.object(SendEmail, "get_subject", lambda s: s.subject)
    mocker.patch.object(SendEmail, "get_body_text", lambda s: s.body_text)
    mocker.patch.object(SendEmail, "get_body_html", lambda s: s.body_html)


@pytest.mark.parametrize(
    "settings_to, expected_to",
    [
        ("to.someone@somewhere.com", "to.someone@somewhere.com"),
        (
            ("to.someone@somewhere.com", "to.someone.2@somewhere.com"),
            "to.someone@somewhere.com, to.someone.2@somewhere.com",
        ),
        (
            " to.someone@somewhere.com, to.someone.2@somewhere.com ",
            "to.someone@somewhere.com, to.someone.2@somewhere.com",
        ),
        (
            "to.someone@somewhere.com,to.someone.2@somewhere.com",
            "to.someone@somewhere.com, to.someone.2@somewhere.com",
        ),
        (
            ["to.someone@somewhere.com", "to.someone.2@somewhere.com"],
            "to.someone@somewhere.com, to.someone.2@somewhere.com",
        ),
    ],
)
def test_email_message_to(mock_render_template, settings_to, expected_to):
    crawler = get_crawler(
        settings_dict={
            "SPIDERMON_EMAIL_SENDER": "from.someone@somewhere.com",
            "SPIDERMON_EMAIL_TO": settings_to,
            "SPIDERMON_EMAIL_SUBJECT": "HERE IS THE TITLE",
            "SPIDERMON_EMAIL_REPLY_TO": "reply.to@somewhere.com",
            "SPIDERMON_BODY_HTML": "some html",
            "SPIDERMON_BODY_TEXT": "some text",
        }
    )
    send_email = SendEmail.from_crawler(crawler)

    message = send_email.get_message()

    assert message["To"] == expected_to


@pytest.mark.parametrize(
    "settings_cc, expected_cc",
    [
        ("cc.someone@somewhere.com", "cc.someone@somewhere.com"),
        (
            ("cc.someone@somewhere.com", "cc.someone.2@somewhere.com"),
            "cc.someone@somewhere.com, cc.someone.2@somewhere.com",
        ),
        (
            " cc.someone@somewhere.com, cc.someone.2@somewhere.com ",
            "cc.someone@somewhere.com, cc.someone.2@somewhere.com",
        ),
        (
            "cc.someone@somewhere.com,cc.someone.2@somewhere.com",
            "cc.someone@somewhere.com, cc.someone.2@somewhere.com",
        ),
        (
            ["cc.someone@somewhere.com", "cc.someone.2@somewhere.com"],
            "cc.someone@somewhere.com, cc.someone.2@somewhere.com",
        ),
    ],
)
def test_email_message_cc(mock_render_template, settings_cc, expected_cc):
    crawler = get_crawler(
        settings_dict={
            "SPIDERMON_EMAIL_SENDER": "from.someone@somewhere.com",
            "SPIDERMON_EMAIL_TO": "to.someone@somewhere.com",
            "SPIDERMON_EMAIL_CC": settings_cc,
            "SPIDERMON_EMAIL_SUBJECT": "HERE IS THE TITLE",
            "SPIDERMON_EMAIL_REPLY_TO": "reply.to@somewhere.com",
            "SPIDERMON_BODY_HTML": "some html",
            "SPIDERMON_BODY_TEXT": "some text",
        }
    )
    send_email = SendEmail.from_crawler(crawler)

    message = send_email.get_message()

    assert message["Cc"] == expected_cc


@pytest.mark.parametrize(
    "settings_bcc, expected_bcc",
    [
        ("bcc.someone@somewhere.com", "bcc.someone@somewhere.com"),
        (
            ("bcc.someone@somewhere.com", "bcc.someone.2@somewhere.com"),
            "bcc.someone@somewhere.com, bcc.someone.2@somewhere.com",
        ),
        (
            " bcc.someone@somewhere.com, bcc.someone.2@somewhere.com ",
            "bcc.someone@somewhere.com, bcc.someone.2@somewhere.com",
        ),
        (
            "bcc.someone@somewhere.com,bcc.someone.2@somewhere.com",
            "bcc.someone@somewhere.com, bcc.someone.2@somewhere.com",
        ),
        (
            ["bcc.someone@somewhere.com", "bcc.someone.2@somewhere.com"],
            "bcc.someone@somewhere.com, bcc.someone.2@somewhere.com",
        ),
    ],
)
def test_email_message_bcc(mock_render_template, settings_bcc, expected_bcc):
    crawler = get_crawler(
        settings_dict={
            "SPIDERMON_EMAIL_SENDER": "from.someone@somewhere.com",
            "SPIDERMON_EMAIL_TO": "to.someone@somewhere.com",
            "SPIDERMON_EMAIL_BCC": settings_bcc,
            "SPIDERMON_EMAIL_SUBJECT": "HERE IS THE TITLE",
            "SPIDERMON_EMAIL_REPLY_TO": "reply.to@somewhere.com",
            "SPIDERMON_BODY_HTML": "some html",
            "SPIDERMON_BODY_TEXT": "some text",
        }
    )
    send_email = SendEmail.from_crawler(crawler)

    message = send_email.get_message()

    assert message["Bcc"] == expected_bcc

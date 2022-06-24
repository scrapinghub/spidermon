import pytest
from scrapy.utils.test import get_crawler

from spidermon.contrib.actions.email.smtp import (
    SendSmtpEmail,
    DEFAULT_SMTP_PORT,
    DEFAULT_SMTP_ENFORCE_SSL,
)
from spidermon.exceptions import NotConfigured


sent_subject = None


@pytest.fixture
def mock_render_template(mocker):
    """Mock functions that render templates to return the raw value"""
    mocker.patch.object(SendSmtpEmail, "get_subject", lambda s: s.subject)
    mocker.patch.object(SendSmtpEmail, "get_body_text", lambda s: s.body_text)
    mocker.patch.object(SendSmtpEmail, "get_body_html", lambda s: s.body_html)


@pytest.fixture
def smtp_action_settings():
    return {
        "SPIDERMON_SMTP_HOST": "smtp.example.com",
        "SPIDERMON_SMTP_USER": "smtp_user",
        "SPIDERMON_SMTP_PASSWORD": "smtp_password",
        "SPIDERMON_SMTP_PORT": DEFAULT_SMTP_PORT,
        "SPIDERMON_SMTP_ENFORCE_SSL": DEFAULT_SMTP_ENFORCE_SSL,
        "SPIDERMON_EMAIL_SENDER": "from@email.xom",
        "SPIDERMON_EMAIL_TO": "to@example.com",
        "SPIDERMON_EMAIL_SUBJECT": "Email Subject",
        "SPIDERMON_EMAIL_REPLY_TO": "reply.to@example.com",
        "SPIDERMON_BODY_HTML": "some html",
        "SPIDERMON_BODY_TEXT": "some text",
        "SPIDERMON_EMAIL_FAKE": False,
    }


def test_use_default_smtp_port_if_not_provided(smtp_action_settings):
    del smtp_action_settings["SPIDERMON_SMTP_PORT"]
    crawler = get_crawler(settings_dict=smtp_action_settings)
    send_smtp_email_action = SendSmtpEmail.from_crawler(crawler)

    assert send_smtp_email_action.smtp_port == DEFAULT_SMTP_PORT


def test_use_configured_smtp_port_when_provided(smtp_action_settings):
    smtp_action_settings["SPIDERMON_SMTP_PORT"] = 465
    crawler = get_crawler(settings_dict=smtp_action_settings)
    send_smtp_email_action = SendSmtpEmail.from_crawler(crawler)

    assert send_smtp_email_action.smtp_port == 465


def test_use_default_smtp_enforce_ssl_if_not_provided(smtp_action_settings):
    del smtp_action_settings["SPIDERMON_SMTP_ENFORCE_SSL"]
    crawler = get_crawler(settings_dict=smtp_action_settings)
    send_smtp_email_action = SendSmtpEmail.from_crawler(crawler)

    assert send_smtp_email_action.smtp_enforce_ssl == DEFAULT_SMTP_ENFORCE_SSL


def test_use_configured_smtp_enforce_ssl_when_provided(smtp_action_settings):
    not_default_smtp_enforce_ssl = not DEFAULT_SMTP_ENFORCE_SSL

    smtp_action_settings["SPIDERMON_SMTP_ENFORCE_SSL"] = not_default_smtp_enforce_ssl
    crawler = get_crawler(settings_dict=smtp_action_settings)
    send_smtp_email_action = SendSmtpEmail.from_crawler(crawler)

    assert send_smtp_email_action.smtp_enforce_ssl == not_default_smtp_enforce_ssl


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
            "SPIDERMON_SMTP_HOST": "smtp.example.com",
            "SPIDERMON_SMTP_USER": "smtp_user",
            "SPIDERMON_SMTP_PASSWORD": "smtp_password",
            "SPIDERMON_EMAIL_SENDER": "from.someone@somewhere.com",
            "SPIDERMON_EMAIL_TO": settings_to,
            "SPIDERMON_EMAIL_SUBJECT": "HERE IS THE TITLE",
            "SPIDERMON_EMAIL_REPLY_TO": "reply.to@somewhere.com",
            "SPIDERMON_BODY_HTML": "some html",
            "SPIDERMON_BODY_TEXT": "some text",
            "SPIDERMON_EMAIL_FAKE": False,
        }
    )

    send_email = SendSmtpEmail.from_crawler(crawler)
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
            "SPIDERMON_SMTP_HOST": "smtp.example.com",
            "SPIDERMON_SMTP_USER": "smtp_user",
            "SPIDERMON_SMTP_PASSWORD": "smtp_password",
            "SPIDERMON_EMAIL_SENDER": "from.someone@somewhere.com",
            "SPIDERMON_EMAIL_TO": "to.someone@somewhere.com",
            "SPIDERMON_EMAIL_CC": settings_cc,
            "SPIDERMON_EMAIL_SUBJECT": "HERE IS THE TITLE",
            "SPIDERMON_EMAIL_REPLY_TO": "reply.to@somewhere.com",
            "SPIDERMON_BODY_HTML": "some html",
            "SPIDERMON_BODY_TEXT": "some text",
            "SPIDERMON_EMAIL_FAKE": False,
        }
    )
    send_email = SendSmtpEmail.from_crawler(crawler)
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
            "SPIDERMON_SMTP_HOST": "smtp.example.com",
            "SPIDERMON_SMTP_USER": "smtp_user",
            "SPIDERMON_SMTP_PASSWORD": "smtp_password",
            "SPIDERMON_EMAIL_SENDER": "from.someone@somewhere.com",
            "SPIDERMON_EMAIL_TO": "to.someone@somewhere.com",
            "SPIDERMON_EMAIL_BCC": settings_bcc,
            "SPIDERMON_EMAIL_SUBJECT": "HERE IS THE TITLE",
            "SPIDERMON_EMAIL_REPLY_TO": "reply.to@somewhere.com",
            "SPIDERMON_BODY_HTML": "some html",
            "SPIDERMON_BODY_TEXT": "some text",
            "SPIDERMON_EMAIL_FAKE": False,
        }
    )
    send_email = SendSmtpEmail.from_crawler(crawler)
    message = send_email.get_message()

    assert message["Bcc"] == expected_bcc


@pytest.mark.parametrize(
    "settings_subject, expected_subject",
    [
        ("Test Subject", "Test Subject"),
        ("Test Subject2", "Test Subject2"),
        ("Test Subject3", "Test Subject3"),
        ("Test Subject4", "Test Subject4"),
        ("Test Subject5", "Test Subject5"),
    ],
)
def test_email_sent(mock_render_template, settings_subject, expected_subject):
    crawler = get_crawler(
        settings_dict={
            "SPIDERMON_SMTP_HOST": "smtp.example.com",
            "SPIDERMON_SMTP_USER": "smtp_user",
            "SPIDERMON_SMTP_PASSWORD": "smtp_password",
            "SPIDERMON_EMAIL_SENDER": "from.someone@somewhere.com",
            "SPIDERMON_EMAIL_TO": "to.someone@somewhere.com",
            "SPIDERMON_EMAIL_SUBJECT": settings_subject,
            "SPIDERMON_EMAIL_REPLY_TO": "reply.to@somewhere.com",
            "SPIDERMON_BODY_HTML": "some html",
            "SPIDERMON_BODY_TEXT": "some text",
            "SPIDERMON_EMAIL_FAKE": False,
        }
    )
    send_email = SendSmtpEmail.from_crawler(crawler)
    send_email.send_message(
        send_email.get_message(), debug=True, _callback=_catch_mail_sent
    )
    assert sent_subject == expected_subject


@pytest.mark.parametrize(
    "missing_setting",
    [
        "SPIDERMON_SMTP_HOST",
        "SPIDERMON_SMTP_USER",
        "SPIDERMON_SMTP_PASSWORD",
    ],
)
def test_raise_not_configured_if_required_setting_not_provided(missing_setting):
    settings = {
        "SPIDERMON_SMTP_HOST": "smtp.example.com",
        "SPIDERMON_SMTP_USER": "smtp_user",
        "SPIDERMON_SMTP_PASSWORD": "smtp_password",
        "SPIDERMON_EMAIL_SENDER": "from.someone@somewhere.com",
        "SPIDERMON_EMAIL_TO": "to.someone@somewhere.com",
        "SPIDERMON_EMAIL_SUBJECT": "HERE IS THE TITLE",
        "SPIDERMON_EMAIL_REPLY_TO": "reply.to@somewhere.com",
        "SPIDERMON_BODY_HTML": "some html",
        "SPIDERMON_BODY_TEXT": "some text",
        "SPIDERMON_SMTP_PORT": 8080,
        "SPIDERMON_SMTP_USER": "test_user",
        "SPIDERMON_SMTP_PASSWORD": "test_password",
    }

    # Remove requred setting so we can test if exception is raised
    del settings[missing_setting]

    crawler = get_crawler(settings_dict=settings)
    with pytest.raises(NotConfigured):
        SendSmtpEmail.from_crawler(crawler)


def _catch_mail_sent(to, subject, body, cc, attach, msg):
    global sent_subject
    sent_subject = subject

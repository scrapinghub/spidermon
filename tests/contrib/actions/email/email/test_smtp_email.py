import pytest

pytest.importorskip("scrapy")

from scrapy.utils.test import get_crawler

from spidermon.contrib.actions.email.smtp import (
    DEFAULT_SMTP_ENFORCE_SSL,
    DEFAULT_SMTP_ENFORCE_TLS,
    DEFAULT_SMTP_PORT,
    SendSmtpEmail,
)
from spidermon.exceptions import NotConfigured

sent_subject = []


@pytest.fixture
def mock_render_template(mocker):
    """Mock functions that render templates to return the raw value"""
    mocker.patch.object(SendSmtpEmail, "get_subject", lambda s: s.subject)
    mocker.patch.object(SendSmtpEmail, "get_body_text", lambda s: s.body_text)
    mocker.patch.object(SendSmtpEmail, "get_body_html", lambda s: s.body_html)


@pytest.fixture(autouse=True)
def mock_mail_sender(mocker):

    class DummyMailSender:
        def __init__(self, *a, **kw):
            pass

        def send(self, to, subject, body, cc=None, _callback=None, **kwargs):
            if _callback:
                _callback(to, subject, body, cc, None, None)

    mocker.patch("spidermon.contrib.actions.email.smtp.MailSender", DummyMailSender)


@pytest.fixture
def smtp_action_settings():
    return {
        "SPIDERMON_SMTP_HOST": "smtp.example.com",
        "SPIDERMON_SMTP_USER": "smtp_user",
        "SPIDERMON_SMTP_PASSWORD": "smtp_password",
        "SPIDERMON_SMTP_PORT": DEFAULT_SMTP_PORT,
        "SPIDERMON_SMTP_ENFORCE_TLS": DEFAULT_SMTP_ENFORCE_TLS,
        "SPIDERMON_SMTP_ENFORCE_SSL": DEFAULT_SMTP_ENFORCE_SSL,
        "SPIDERMON_EMAIL_SENDER": "from@example.com",
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


def test_use_default_smtp_enforce_tls_if_not_provided(smtp_action_settings):
    del smtp_action_settings["SPIDERMON_SMTP_ENFORCE_TLS"]
    crawler = get_crawler(settings_dict=smtp_action_settings)
    send_smtp_email_action = SendSmtpEmail.from_crawler(crawler)

    assert send_smtp_email_action.smtp_enforce_tls == DEFAULT_SMTP_ENFORCE_TLS


def test_use_configured_smtp_enforce_tls_when_provided(smtp_action_settings):
    not_default_smtp_enforce_tls = not DEFAULT_SMTP_ENFORCE_TLS

    smtp_action_settings["SPIDERMON_SMTP_ENFORCE_TLS"] = not_default_smtp_enforce_tls
    crawler = get_crawler(settings_dict=smtp_action_settings)
    send_smtp_email_action = SendSmtpEmail.from_crawler(crawler)

    assert send_smtp_email_action.smtp_enforce_tls == not_default_smtp_enforce_tls


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
    ("setting", "attribute"),
    [
        ("SPIDERMON_SMTP_HOST", "smtp_host"),
        ("SPIDERMON_SMTP_USER", "smtp_user"),
        ("SPIDERMON_SMTP_PASSWORD", "smtp_password"),
        ("SPIDERMON_SMTP_PORT", "smtp_port"),
        ("SPIDERMON_SMTP_ENFORCE_SSL", "smtp_enforce_ssl"),
    ],
)
def test_set_provided_smtp_settings(setting, attribute, smtp_action_settings):
    crawler = get_crawler(settings_dict=smtp_action_settings)
    send_smtp_email = SendSmtpEmail.from_crawler(crawler)
    assert getattr(send_smtp_email, attribute) == smtp_action_settings[setting]


@pytest.mark.parametrize(
    ("settings_subject", "expected_subject"),
    [
        ("Test Subject", "Test Subject"),
        ("Test Subject2", "Test Subject2"),
        ("Test Subject3", "Test Subject3"),
        ("Test Subject4", "Test Subject4"),
        ("Test Subject5", "Test Subject5"),
    ],
)
def test_email_sent(
    mock_render_template,
    settings_subject,
    expected_subject,
    smtp_action_settings,
):
    smtp_action_settings["SPIDERMON_EMAIL_SUBJECT"] = settings_subject

    crawler = get_crawler(settings_dict=smtp_action_settings)
    send_email = SendSmtpEmail.from_crawler(crawler)
    send_email.send_message(
        send_email.get_message(),
        debug=True,
        _callback=_catch_mail_sent,
    )
    assert sent_subject[-1] == expected_subject


@pytest.mark.parametrize(
    "missing_setting",
    [
        "SPIDERMON_SMTP_HOST",
        "SPIDERMON_SMTP_USER",
        "SPIDERMON_SMTP_PASSWORD",
    ],
)
def test_raise_not_configured_if_required_setting_not_provided(
    smtp_action_settings,
    missing_setting,
):
    # Remove requred setting so we can test if exception is raised
    del smtp_action_settings[missing_setting]

    crawler = get_crawler(settings_dict=smtp_action_settings)
    with pytest.raises(NotConfigured):
        SendSmtpEmail.from_crawler(crawler)


def _catch_mail_sent(to, subject, body, cc, attach, msg):  # noqa: PLR0913
    sent_subject.append(subject)

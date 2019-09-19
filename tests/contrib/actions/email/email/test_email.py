import pytest
from scrapy.utils.test import get_crawler

from spidermon.contrib.actions.email import SendEmail


class SendEmailTest(SendEmail):
    """A helper class to override the base class behavior of formatting templates.
    This way no setup is required for a simple test."""

    def get_subject(self):
        return self.subject

    def get_body_text(self):
        return self.body_text

    def get_body_html(self):
        return self.body_html


@pytest.mark.parametrize(
    "settings, expected",
    [
        (
            {
                "from": "from.someone@somewhere.com",
                "to": "to.someone@somewhere.com",
                "cc": "cc.someone@somewhere.com",
                "bcc": "bcc.someone@somewhere.com",
            },
            {
                "from": "from.someone@somewhere.com",
                "to": "to.someone@somewhere.com",
                "cc": "cc.someone@somewhere.com",
                "bcc": "bcc.someone@somewhere.com",
            },
        ),
        (
            {
                "from": "from.someone@somewhere.com",
                "to": "to.someone@somewhere.com,to.someone.2@somewhere.com",
                "cc": "cc.someone@somewhere.com,cc.someone.2@somewhere.com",
                "bcc": "bcc.someone@somewhere.com,bcc.someone.2@somewhere.com",
            },
            {
                "from": "from.someone@somewhere.com",
                "to": "to.someone@somewhere.com, to.someone.2@somewhere.com",
                "cc": "cc.someone@somewhere.com, cc.someone.2@somewhere.com",
                "bcc": "bcc.someone@somewhere.com, bcc.someone.2@somewhere.com",
            },
        ),
        (
            {
                "from": "from.someone@somewhere.com",
                "to": ["to.someone@somewhere.com", "to.someone.2@somewhere.com"],
                "cc": ["cc.someone@somewhere.com", "cc.someone.2@somewhere.com"],
                "bcc": ["bcc.someone@somewhere.com", "bcc.someone.2@somewhere.com"],
            },
            {
                "from": "from.someone@somewhere.com",
                "to": "to.someone@somewhere.com, to.someone.2@somewhere.com",
                "cc": "cc.someone@somewhere.com, cc.someone.2@somewhere.com",
                "bcc": "bcc.someone@somewhere.com, bcc.someone.2@somewhere.com",
            },
        ),
        (
            {
                "from": "from.someone@somewhere.com",
                "to": ("to.someone@somewhere.com", "to.someone.2@somewhere.com"),
                "cc": ("cc.someone@somewhere.com", "cc.someone.2@somewhere.com"),
                "bcc": ("bcc.someone@somewhere.com", "bcc.someone.2@somewhere.com"),
            },
            {
                "from": "from.someone@somewhere.com",
                "to": "to.someone@somewhere.com, to.someone.2@somewhere.com",
                "cc": "cc.someone@somewhere.com, cc.someone.2@somewhere.com",
                "bcc": "bcc.someone@somewhere.com, bcc.someone.2@somewhere.com",
            },
        ),
        (
            {
                "from": "from.someone@somewhere.com",
                "to": ("to.someone@somewhere.com", "to.someone.2@somewhere.com"),
                "cc": None,
                "bcc": None,
            },
            {
                "from": "from.someone@somewhere.com",
                "to": "to.someone@somewhere.com, to.someone.2@somewhere.com",
                "cc": None,
                "bcc": None,
            },
        ),
    ],
)
def test_email_message_to_from_cc_bcc(settings, expected):
    crawler = get_crawler(
        settings_dict={
            "SPIDERMON_EMAIL_SENDER": settings["from"],
            "SPIDERMON_EMAIL_TO": settings["to"],
            "SPIDERMON_EMAIL_CC": settings["cc"],
            "SPIDERMON_EMAIL_BCC": settings["bcc"],
            "SPIDERMON_EMAIL_SUBJECT": "HERE IS THE TITLE",
            "SPIDERMON_EMAIL_REPLY_TO": "reply.to@somewhere.com",
            "SPIDERMON_BODY_HTML": "some html",
            "SPIDERMON_BODY_TEXT": "some text",
        }
    )
    send_email = SendEmailTest.from_crawler(crawler)

    message = send_email.get_message()

    assert message["From"] == expected["from"]
    assert message["To"] == expected["to"]
    assert message["Cc"] == expected["cc"]
    assert message["Bcc"] == expected["bcc"]

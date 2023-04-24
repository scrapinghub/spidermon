import ast
import json
import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from spidermon.contrib.actions.templates import ActionWithTemplates
from spidermon.exceptions import NotConfigured

logger = logging.getLogger(__name__)


class SlackMessageManager:
    sender_token = None
    sender_name = None

    def __init__(self, sender_token=None, sender_name=None, fake=False):
        sender_token = sender_token or self.sender_token
        if not sender_token:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_SLACK_SENDER_TOKEN setting."
            )

        self.sender_name = sender_name or self.sender_name
        if not self.sender_name:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_SLACK_SENDER_NAME setting."
            )

        self.fake = fake
        self._client = WebClient(sender_token)
        self._users = None

    @property
    def users(self):
        if self._users is None:
            self._users = self._get_users_info()
        return self._users

    def send_message(
        self,
        to,
        text,
        parse=None,
        link_names=1,
        attachments=None,
        use_mention=False,
        **kwargs,
    ):
        if self.fake:
            logger.info(text)
            if attachments:
                logger.info(attachments)
            return

        if isinstance(to, list):
            return [
                self.send_message(
                    to=recipient,
                    text=text,
                    parse=parse,
                    link_names=link_names,
                    attachments=attachments,
                    use_mention=use_mention,
                    **kwargs,
                )
                for recipient in to
            ]
        elif to.startswith("@"):
            return self._send_user_message(
                username=to,
                text=text,
                parse=parse,
                link_names=link_names,
                attachments=attachments,
                **kwargs,
            )
        else:
            if use_mention:
                if to.startswith("#"):
                    text = "@channel: " + text
                else:
                    text = "@group: " + text
            return self._send_channel_message(
                channel=to,
                text=text,
                parse=parse,
                link_names=link_names,
                attachments=attachments,
                **kwargs,
            )

    def _get_user_id(self, username):
        name = username[1:] if username.startswith("@") else username
        user = self.users.get(name, None)
        return user["id"] if user else None

    def _get_users_info(self):
        return dict(
            [
                (member["name"].lower(), member)
                for member in self._client.users_list()["members"]
            ]
        )

    def _send_user_message(
        self, username, text, parse="full", link_names=1, attachments=None, **kwargs
    ):
        user_id = self._get_user_id(username)
        if user_id:
            return self._send_channel_message(
                channel=user_id,
                text=text,
                parse=parse,
                link_names=link_names,
                attachments=attachments,
                **kwargs,
            )

    def _send_channel_message(
        self, channel, text, parse="full", link_names=1, attachments=None, **kwargs
    ):
        self._client.chat_postMessage(
            channel=channel,
            text=text,
            parse=parse,
            link_names=link_names,
            attachments=self._parse_attachments(attachments),
            username=self.sender_name,
            icon_url=self._get_icon_url(),
            **kwargs,
        )

    def _get_icon_url(self):
        """
        Looks up the icon url for the user set as the message sender

        This will only return a URL if the slack app has users:read permission and
        bot appears in the organisation user list. A no frills bot intended to
        just send messages is not likely to fulfill these criteria, so it returns
        None in this situation, which will result in slack using the bot's App Icon.
        """
        try:
            icon_url = self.users[self.sender_name]["profile"]["image_48"]
        except SlackApiError as e:
            if (
                e.response.data.get("error") == "missing_scope"
                and e.response.data.get("needed") == "users:read"
            ):
                logger.warning(
                    f"bot does not have users:read permissions for slack org - default icon url used"
                )
                # can be an expected outcome - will use its own icon
                icon_url = None
            else:
                raise e
        except KeyError:
            # bot has read permissions for slack org but can't find sender in list
            # can be an expected outcome - will use its own icon
            logger.warning(
                f"bot cannot finder user in slack org member list - default icon url used"
            )
            icon_url = None
        return icon_url

    def _parse_attachments(self, attachments):
        if not attachments:
            return None
        else:
            python_attachments = ast.literal_eval(attachments)
            return json.dumps(python_attachments)


class SendSlackMessage(ActionWithTemplates):
    message = None
    attachments = None
    message_template = "slack/default/message.jinja"
    attachments_template = "slack/default/attachments.jinja"
    recipients = None
    sender_token = None
    sender_name = None
    include_message = True
    include_attachments = True
    fake = False

    def __init__(
        self,
        sender_token=None,
        sender_name=None,
        recipients=None,
        message=None,
        message_template=None,
        include_message=None,
        attachments=None,
        attachments_template=None,
        include_attachments=None,
        fake=None,
        **kwargs,
    ):
        super().__init__()

        self.fake = fake or self.fake
        self.manager = SlackMessageManager(
            sender_token=sender_token or self.sender_token,
            sender_name=sender_name or self.sender_name,
            fake=self.fake,
        )

        self.recipients = recipients or self.recipients
        self.message = message or self.message
        self.message_template = message_template or self.message_template

        if include_message is not None:
            self.include_message = include_message

        if include_attachments is not None:
            self.include_attachments = include_attachments

        self.attachments = attachments or self.attachments
        self.attachments_template = attachments_template or self.attachments_template

        self.kwargs = kwargs or {}

        if not self.fake and not self.recipients:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_SLACK_RECIPIENTS setting."
            )

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        return {
            "sender_token": crawler.settings.get("SPIDERMON_SLACK_SENDER_TOKEN"),
            "sender_name": crawler.settings.get("SPIDERMON_SLACK_SENDER_NAME"),
            "recipients": crawler.settings.getlist("SPIDERMON_SLACK_RECIPIENTS"),
            "message": crawler.settings.get("SPIDERMON_SLACK_MESSAGE"),
            "message_template": crawler.settings.get(
                "SPIDERMON_SLACK_MESSAGE_TEMPLATE"
            ),
            "attachments": crawler.settings.get("SPIDERMON_SLACK_ATTACHMENTS"),
            "attachments_template": crawler.settings.get(
                "SPIDERMON_SLACK_ATTACHMENTS_TEMPLATE"
            ),
            "include_message": crawler.settings.get("SPIDERMON_SLACK_INCLUDE_MESSAGE"),
            "include_attachments": crawler.settings.get(
                "SPIDERMON_SLACK_INCLUDE_ATTACHMENTS"
            ),
            "fake": crawler.settings.getbool("SPIDERMON_SLACK_FAKE"),
        }

    def run_action(self):
        self.manager.send_message(
            to=self.recipients,
            text=self.get_message(),
            attachments=self.get_attachments(),
            **self.kwargs,
        )

    def get_message(self):
        if self.include_message:
            if self.message:
                return self.render_text_template(self.message)
            else:
                return self.render_template(self.message_template)
        else:
            return None

    def get_attachments(self):
        if self.include_attachments:
            if self.attachments:
                return self.render_text_template(self.attachments)
            else:
                return self.render_template(self.attachments_template)
        else:
            return None

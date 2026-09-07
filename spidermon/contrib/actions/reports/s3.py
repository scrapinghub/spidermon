import secrets
from pathlib import Path

import boto3

from spidermon.exceptions import NotConfigured
from spidermon.utils.settings import get_aws_credentials

from . import CreateReport

DEFAULT_S3_REGION_ENDPOINT = "s3.amazonaws.com"
DEFAULT_S3_CONTENT_TYPE = "text/html"

_HEADER_TO_EXTRA_ARG = {"Content-Type": "ContentType"}


class S3Uploader:
    def __init__(self, aws_key, aws_secret):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
        )

    def upload_from_file(
        self,
        source_filename,
        s3_bucket,
        s3_filename,
        headers=None,
        make_public=False,
    ):
        with Path(source_filename).open("rb") as f:
            self._upload(
                bucket=s3_bucket,
                filename=s3_filename,
                body=f,
                headers=headers,
                make_public=make_public,
            )

    def upload_from_content(
        self,
        content,
        s3_bucket,
        s3_filename,
        headers=None,
        make_public=False,
    ):
        if isinstance(content, str):
            content = content.encode("utf-8")
        self._upload(
            bucket=s3_bucket,
            filename=s3_filename,
            body=content,
            headers=headers,
            make_public=make_public,
        )

    def _upload(self, bucket, filename, body, headers=None, make_public=False):
        extra_args = {
            _HEADER_TO_EXTRA_ARG[name]: value
            for name, value in (headers or {}).items()
            if name in _HEADER_TO_EXTRA_ARG
        }
        if make_public:
            extra_args["ACL"] = "public-read"
        self.client.put_object(Bucket=bucket, Key=filename, Body=body, **extra_args)


class CreateS3Report(CreateReport):
    aws_access_key = None
    aws_secret_key = None
    s3_bucket = None
    s3_filename = None
    s3_region_endpoint = DEFAULT_S3_REGION_ENDPOINT
    make_public = True
    content_type = DEFAULT_S3_CONTENT_TYPE

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        aws_access_key=None,
        aws_secret_key=None,
        s3_bucket=None,
        s3_filename=None,
        s3_region_endpoint=None,
        make_public=False,
        content_type=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.aws_access_key = aws_access_key or self.aws_access_key
        self.aws_secret_key = aws_secret_key or self.aws_secret_key
        self.s3_bucket = s3_bucket or self.s3_bucket
        self.s3_region_endpoint = s3_region_endpoint or self.s3_region_endpoint
        self.s3_filename = s3_filename or self.s3_filename
        self.make_public = make_public or self.make_public
        self.content_type = content_type or self.content_type
        self._url_secret = secrets.token_hex(16)
        if not self.aws_access_key:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_AWS_ACCESS_KEY_ID setting.",
            )
        if not self.aws_secret_key:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_AWS_SECRET_ACCESS_KEY setting.",
            )
        if not self.s3_bucket:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_REPORT_S3_BUCKET setting.",
            )
        if not self.s3_filename:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_REPORT_S3_FILENAME setting.",
            )

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super().from_crawler_kwargs(crawler)
        (aws_access_key_id, aws_secret_access_key) = get_aws_credentials(
            crawler.settings,
        )
        kwargs.update(
            {
                "aws_access_key": aws_access_key_id,
                "aws_secret_key": aws_secret_access_key,
                "s3_bucket": crawler.settings.get("SPIDERMON_REPORT_S3_BUCKET"),
                "s3_filename": crawler.settings.get("SPIDERMON_REPORT_S3_FILENAME"),
                "s3_region_endpoint": crawler.settings.get(
                    "SPIDERMON_REPORT_S3_REGION_ENDPOINT",
                ),
                "make_public": crawler.settings.get("SPIDERMON_REPORT_S3_MAKE_PUBLIC"),
                "content_type": crawler.settings.get(
                    "SPIDERMON_REPORT_S3_CONTENT_TYPE",
                ),
            },
        )
        return kwargs

    def after_render_report(self):
        s3 = S3Uploader(self.aws_access_key, self.aws_secret_key)
        s3.upload_from_content(
            content=self.report,
            s3_bucket=self.s3_bucket,
            s3_filename=self.get_s3_filename(),
            headers={"Content-Type": self.content_type},
            make_public=self.make_public,
        )

    def get_s3_filename(self):
        return f"reports/{self.get_url_secret()}/{self.render_text_template(self.s3_filename)}"

    def get_s3_report_url(self):
        return f"https://{self.s3_region_endpoint}/{self.s3_bucket}/{self.get_s3_filename()}"

    def get_url_secret(self):
        return self._url_secret

    def get_meta(self):
        report_url = self.get_s3_report_url()
        return {"reports_links": [*self.data.meta.get("reports", []), report_url]}

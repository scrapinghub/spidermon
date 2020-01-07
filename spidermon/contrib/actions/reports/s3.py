from __future__ import absolute_import
import hashlib

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from spidermon.exceptions import NotConfigured

from . import CreateReport


DEFAULT_S3_REGION_ENDPOINT = "s3.amazonaws.com"
DEFAULT_S3_CONTENT_TYPE = "text/html"
URL_SECRET_KEY = "The secret to life the universe and everything"


class S3Uploader(object):
    def __init__(self, aws_key, aws_secret):
        self.connection = S3Connection(
            aws_access_key_id=aws_key, aws_secret_access_key=aws_secret
        )

    def upload_from_file(
        self, source_filename, s3_bucket, s3_filename, headers=None, make_public=False
    ):
        with open(source_filename, "r") as f:
            self._upload_with_method(
                bucket=s3_bucket,
                method_name="set_contents_from_file",
                filename=s3_filename,
                content=f,
                headers=headers,
                make_public=make_public,
            )

    def upload_from_content(
        self, content, s3_bucket, s3_filename, headers=None, make_public=False
    ):
        self._upload_with_method(
            bucket=s3_bucket,
            method_name="set_contents_from_string",
            filename=s3_filename,
            content=content,
            headers=headers,
            make_public=make_public,
        )

    def _upload_with_method(
        self, bucket, method_name, filename, content, headers=None, make_public=False
    ):
        # Get bucket without validation (Needed to be used with credentials w/o listing perms)
        bucket = self.connection.get_bucket(bucket, validate=False)
        f = Key(bucket)
        f.key = filename
        getattr(f, method_name)(content, headers=headers)
        if make_public:
            f.make_public()


class CreateS3Report(CreateReport):
    aws_access_key = None
    aws_secret_key = None
    s3_bucket = None
    s3_filename = None
    s3_region_endpoint = DEFAULT_S3_REGION_ENDPOINT
    make_public = True
    content_type = DEFAULT_S3_CONTENT_TYPE

    def __init__(
        self,
        aws_access_key=None,
        aws_secret_key=None,
        s3_bucket=None,
        s3_filename=None,
        s3_region_endpoint=None,
        make_public=False,
        content_type=None,
        *args,
        **kwargs
    ):
        super(CreateS3Report, self).__init__(*args, **kwargs)

        self.aws_access_key = aws_access_key or self.aws_access_key
        self.aws_secret_key = aws_secret_key or self.aws_secret_key
        self.s3_bucket = s3_bucket or self.s3_bucket
        self.s3_region_endpoint = s3_region_endpoint or self.s3_region_endpoint
        self.s3_filename = s3_filename or self.s3_filename
        self.make_public = make_public or self.make_public
        self.content_type = content_type or self.content_type
        if not self.aws_access_key:
            raise NotConfigured("You must provide the AWS Access Key.")
        if not self.aws_secret_key:
            raise NotConfigured("You must provide the AWS Secret Key.")
        if not self.s3_bucket:
            raise NotConfigured("You must define the s3 bucket.")
        if not self.s3_filename:
            raise NotConfigured("You must define the s3 filename.")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(CreateS3Report, cls).from_crawler_kwargs(crawler)
        (aws_access_key_id, aws_secret_access_key) = get_aws_credentials(
            crawler.settings
        )
        kwargs.update(
            {
                "aws_access_key": aws_access_key_id,
                "aws_secret_key": aws_secret_access_key,
                "s3_bucket": crawler.settings.get("SPIDERMON_REPORT_S3_BUCKET"),
                "s3_filename": crawler.settings.get("SPIDERMON_REPORT_S3_FILENAME"),
                "s3_region_endpoint": crawler.settings.get(
                    "SPIDERMON_REPORT_S3_REGION_ENDPOINT"
                ),
                "make_public": crawler.settings.get("SPIDERMON_REPORT_S3_MAKE_PUBLIC"),
                "content_type": crawler.settings.get(
                    "SPIDERMON_REPORT_S3_CONTENT_TYPE"
                ),
            }
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
        return "reports/{secret}/{filename}".format(
            secret=self.get_url_secret(),
            filename=self.render_text_template(self.s3_filename),
        )

    def get_s3_report_url(self):
        return "https://{region}/{bucket}/{filename}".format(
            region=self.s3_region_endpoint,
            bucket=self.s3_bucket,
            filename=self.get_s3_filename(),
        )

    def get_url_secret(self):
        secret = URL_SECRET_KEY
        if self.data.job:
            secret += str(self.data.job.key.split("/")[0])
        return hashlib.md5(secret.encode()).hexdigest()

    def get_meta(self):
        report_url = self.get_s3_report_url()
        return {"reports_links": self.data.meta.get("reports", []) + [report_url]}

#!/bin/sh
s3cmd sync setacl --acl-public --recursive img/ s3://email-templates.scrapinghub.com/spidermon/
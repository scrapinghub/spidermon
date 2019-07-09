import click

from functools import wraps
from scrapy.utils.project import inside_project
from spidermon.commands.prompts import monitor_prompts


def is_inside_project(command):
    @wraps(command)
    def wrapper_is_inside_project(*args, **kwargs):
        if not inside_project():
            click.echo(monitor_prompts["project_error"])
        else:
            command(*args, **kwargs)

    return wrapper_is_inside_project

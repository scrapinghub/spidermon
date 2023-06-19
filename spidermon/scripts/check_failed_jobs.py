import logging

from argparse import ArgumentParser
from datetime import datetime, timedelta
from scrapinghub import Project, Connection

logger = logging.getLogger()


class CheckFailedJobs:
    def __init__(self):
        self.args = self.parse_args()

    def __enter__(self):
        return self

    def __exit__(self, typ, val, traceback):
        if len(self.failed_jobs) > 0:
            for job in self.failed_jobs:
                logger.error(f"Job {job.info.get('id')} has close    reason 'failed'.")
        logger.info("Finished checking job failures.")
        return

    def parse_args(self):
        parser = ArgumentParser()
        parser.add_argument("--api-key")
        parser.add_argument("--project-id")
        parser.add_argument(
            "--lookback",
            help="How far back (in hours) the script should look for failed jobs.",
            type=int,
        )

        args = parser.parse_args()

        if not args.api_key:
            parser.error("Please provide an API key with the --api-key option.")

        if not args.project_id:
            parser.error("Please provide a project id with the --project-id option.")

        if not args.lookback:
            parser.error("Please provide a lookback with the --lookback option.")

        return args

    def get_failed_jobs(self):
        project = Project(Connection(self.args.api_key), self.args.project_id)
        since_time = datetime.utcnow() - timedelta(hours=self.args.lookback)
        jobs = [
            job
            for job in project.jobs(state="finished")
            if since_time
            <= datetime.strptime(job.info["updated_time"], "%Y-%m-%dT%H:%M:%S")
            and job.info.get("close_reason") == "failed"
        ]
        return jobs

    def run(self):
        self.failed_jobs = self.get_failed_jobs()

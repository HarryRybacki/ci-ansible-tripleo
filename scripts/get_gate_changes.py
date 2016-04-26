#!/usr/bin/env python

"""
Fetch changes from gerrit servers and apply them on git repos.

The instance name should be defined in the script's ALLOWED_HOSTS
variable.
"""

import logging
import os
import shlex
import subprocess
from argparse import ArgumentParser

# we ignore any other host reference
ALLOWED_HOSTS = ["review.gerrithub.io"]


def parse_env_variables():
    """Look for dependency links in the commit message."""

    project = os.environ.get("GERRIT_PROJECT")
    refspec = os.environ.get("GERRIT_REFSPEC")
    host = os.environ.get("GERRIT_HOST")

    if not all([project, refspec, host]):
        logging.warning(
            "GERRIT_HOST [{}], GERRIT_PROJECT [{}], GERRIT_REFSPEC [{}] have to be set".format(
                host, project, refspec)
        )
        return ()
    if host not in ALLOWED_HOSTS:
        logging.warning("GERRIT_HOST not allowed")
        return()
    return host, project, refspec


def update_repo(basedir, host, project, refspec):
    """
    With the change, host and project known we do a fetch to that refspec
    there's one caveat at this moment. we assume project variable is in the
    form of <org>/<projectname> and that the git checkouted version is on the
    <basedir>/<projectname>
    """

    remote_cmd = "git fetch https://{}/{} {}".format(host, project, refspec)
    fetch_cmd = "git checkout FETCH_HEAD"
    try:
        project_folder = project.split("/")[1]
        folder_path = os.path.join(basedir, project_folder)
        logging.debug("changing working dir to %s", folder_path)
        os.chdir(folder_path)
        logging.debug("running %s", remote_cmd)
        subprocess.Popen(shlex.split(remote_cmd)).wait()
        logging.debug("running fetch %s", fetch_cmd)
        subprocess.Popen(shlex.split(fetch_cmd)).wait()
    except OSError:
        logging.warning(
            "Directory not found for {} skipping".format(project)
        )


def run(basedir):
    """ Given a basedir arse the variables and fetch the changes """

    logging.warning(
        "getting git changes"
    )
    change = parse_env_variables()
    if change:
        update_repo(basedir, *change)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ap = ArgumentParser(
        "Generate changes to repos or rpm settings based on depends-on gerrit comments"
    )
    ap.add_argument('basedir',
                    default=".",
                    help="basedir to work from")
    args = ap.parse_args()
    run(args.basedir)

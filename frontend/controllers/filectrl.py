#
# Copyright (c) 2013-2015 QuarksLab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

from frontend.models.sqlobjects import File
from frontend.helpers.sessions import session_transaction
from frontend.helpers.utils import write_attachment_on_disk


# used by tasks.py
def remove_files(max_age_sec):
    with session_transaction() as session:
        return File.remove_old_files(max_age_sec, session)


def add_attachment(sha256, files):
    """ add attachment(s) to the file specified by sha256

    :param sha256: file sha256
    :param files: dict of 'filename':str, 'data':str
    :rtype: int
    :return: int - total number of files for the scan
    """
    for (name, data) in files.items():
        write_attachment_on_disk(sha256, name, data)

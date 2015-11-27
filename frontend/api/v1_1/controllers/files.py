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

import os
import frontend.controllers.filectrl as file_ctrl
from bottle \
    import response, request
from frontend.api.v1_1.errors \
    import process_error
from frontend.helpers.utils \
    import delete_attachment_on_disk, list_attachments_on_disk


def add_attachments(sha256):
    """ Attach a file to a scan.
        The request should be performed using a POST request method.
    """
    try:
        files = {}
        filenames = []
        for f in request.files:
            upfile = request.files.get(f)
            filename = os.path.basename(upfile.filename)
            data = upfile.file.read()
            files[filename] = data
            filenames.append(filename)

        file_ctrl.add_attachment(sha256, files)

        response.content_type = "application/json; charset=UTF-8"
        return {
            "total": len(filenames),
            "data": filenames
        }
    except Exception as e:
        process_error(e)


def delete_attachment(sha256, attachment):
    """ Delete an attachment of a file
    """
    try:
        deleted_attachment = delete_attachment_on_disk(sha256, attachment)

        response.content_type = "application/json; charset=UTF-8"
        return {
            "total": len(deleted_attachment),
            "data": deleted_attachment
        }
    except Exception as e:
        process_error(e)


def list_attachments(sha256):
    """ List all attachment of a file.
    """
    try:
        attachment_list = list_attachments_on_disk(sha256)

        response.content_type = "application/json; charset=UTF-8"

        return {
            "total": len(attachment_list),
            "data": attachment_list
        }
    except Exception as e:
        process_error(e)


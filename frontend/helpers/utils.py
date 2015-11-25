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

import re
import os

import config.parser as config
from lib.common.utils import UUID
from lib.irma.common.exceptions import IrmaValueError, IrmaFileSystemError


def validate_id(ext_id):
    """ check external_id format - should be a str(ObjectId)"""
    if not UUID.validate(ext_id):
        raise ValueError("Malformed id")


def validate_sha256(sha256):
    """ check hashvalue format - should be a sha256 hexdigest"""
    if not re.match(r'^[0-9a-fA-F]{64}$', sha256):
        raise ValueError("Malformed Sha256")


def validate_sha1(sha1):
    """ check hashvalue format - should be a sha1 hexdigest"""
    if not re.match(r'^[0-9a-fA-F]{40}$', sha1):
        raise ValueError("Malformed Sha1")


def validate_md5(md5):
    """ check hashvalue format - should be a md5 hexdigest"""
    if not re.match(r'^[0-9a-fA-F]{32}$', md5):
        raise ValueError("Malformed md5")


def guess_hash_type(value):
    """ guess which kind of hash is given as parameter """
    hash_type = None

    # We use hash length as hash index to speed up lookups
    hash_dict = {
        32: ("md5", validate_md5),
        40: ("sha1", validate_sha1),
        64: ("sha256", validate_sha256),
    }

    str_length = len(str(value))
    if str_length in hash_dict.keys():
        validate = hash_dict[str_length][1]
        hash_str = hash_dict[str_length][0]
        try:
            validate(value)
            hash_type = hash_str
        except ValueError:
            pass
    return hash_type


# helper to split files in subdirs
def build_sha256_path(sha256):
    """Builds a file path from its sha256. Creates directory if needed.
    :param sha256: the sha256 to create path
    :rtype: string
    :return: the path build from the sha256
    :raise: IrmaValueError, IrmaFileSystemError
        """
    PREFIX_NB = 3
    PREFIX_LEN = 2
    base_path = config.get_samples_storage_path()
    if (PREFIX_NB * PREFIX_LEN) > len(sha256):
        raise IrmaValueError("too much prefix for file storage")
    path = base_path
    for i in xrange(0, PREFIX_NB):
        prefix = sha256[i * PREFIX_LEN: (i + 1) * PREFIX_LEN]
        path = os.path.join(path, prefix)
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.isdir(path):
        reason = "storage path is not a directory"
        raise IrmaFileSystemError(reason)
    return os.path.join(path, sha256)


def write_sample_on_disk(sha256, data):
    """Write sample data on the location calculated from file sha256
    :param sha256: the file's sha256
    :param data: the file's data
    :rtype: string
    :return: the path build from the sha256
    :raise: IrmaFileSystemError
    """
    path = build_sha256_path(sha256)
    try:
        with open(path, 'wb') as filee:
            filee.write(data)
    except IOError:
        raise IrmaFileSystemError(
            'Cannot add the sample {0} to the collection'.format(sha256)
        )
    return path


def write_attachment_on_disk(sha256, name, data):
    """Write attachment data on the location calculated from sample sha256
    :param sha256: the file's sha256
    :param data: the file's data
    :rtype: string
    :return: the path build from the sha256
    :raise: IrmaFileSystemError
    """
    base_path = config.get_attachments_storage_path()
    path = os.path.join(base_path, sha256)
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.isdir(path):
        reason = "storage path is not a directory"
        raise IrmaFileSystemError(reason)
    try:
        with open(os.path.join(path, name), 'wb') as filee:
            filee.write(data)
    except IOError:
        raise IrmaFileSystemError(
            'Cannot add attachment {0} for sample {0}'.format(name, sha256)
        )
    return path


def delete_attachment_on_disk(sha256, name):
    """Delete attachment from sample sha256
    :param sha256: the file's sha256
    :param name: the attachment file name to delete
    :rtype: int
    :return: number of deleted file (1 or 0)
    :raise: IrmaFileSystemError
    """
    files_deleted = []

    base_path = config.get_attachments_storage_path()
    path = os.path.join(base_path, sha256)
    if not os.path.exists(path):
        reason = "attachment storage path does not exist"
        raise IrmaFileSystemError(reason)
    try:
        os.remove(os.path.join(path, name))
        files_deleted.append(name)
    except IOError:
        raise IrmaFileSystemError(
            'Cannot add attachment {0} for sample {0}'.format(name, sha256)
        )
    return files_deleted


def list_attachments_on_disk(sha256):
    """List all the attachments on the diskl for sample sha256
    :param sha256: the file's sha256
    :rtype: list
    :return: list of filenames in /<sha256>/
    :raise: IrmaFileSystemError
    """
    base_path = config.get_attachments_storage_path()
    path = os.path.join(base_path, sha256)
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        only_files = [
            f for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
            ]
    except Exception:
        raise IrmaFileSystemError(
            'Cannot list attachment for file {0}'.format(sha256)
        )
    return only_files

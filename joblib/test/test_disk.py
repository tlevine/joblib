"""
Unit tests for the disk utilities.
"""

# Authors: Gael Varoquaux <gael dot varoquaux at normalesup dot org>
#          Lars Buitinck
# Copyright (c) 2010 Gael Varoquaux
# License: BSD Style, 3 clauses.

from __future__ import with_statement

import os
import shutil
import array
from tempfile import mkdtemp

import nose

from joblib.disk import disk_used, memstr_to_bytes, mkdirp


###############################################################################

def test_disk_used():
    cachedir = mkdtemp()
    try:
        if os.path.exists(cachedir):
            shutil.rmtree(cachedir)
        os.mkdir(cachedir)
        # Not write a file that is 1M big in this directory, and check the
        # size. The reason we use such a big file is that it makes us robust
        # to errors due to block allocation.
        a = array.array('i')
        sizeof_i = a.itemsize
        target_size = 1024

        # We set a buffer because sometimes the
        buffer_ = 48 # This is enough on an OpenBSD Fast File System.

        n = int(target_size * 1024 / sizeof_i)
        a = array.array('i', n * (1,))
        with open(os.path.join(cachedir, 'test'), 'wb') as output:
            a.tofile(output)
        nose.tools.assert_true(disk_used(cachedir) >= target_size)
        nose.tools.assert_true(disk_used(cachedir) < target_size + buffer_)
    finally:
        shutil.rmtree(cachedir)


def test_memstr_to_bytes():
    for text, value in zip(('80G', '1.4M', '120M', '53K'),
                           (80 * 1024 ** 3, int(1.4 * 1024 ** 2),
                            120 * 1024 ** 2, 53 * 1024)):
        yield nose.tools.assert_equal, memstr_to_bytes(text), value

    nose.tools.assert_raises(ValueError, memstr_to_bytes, 'foobar')


def test_mkdirp():
    try:
        tmp = mkdtemp()

        mkdirp(os.path.join(tmp, "ham"))
        mkdirp(os.path.join(tmp, "ham"))
        mkdirp(os.path.join(tmp, "spam", "spam"))

        # Not all OSErrors are ignored
        nose.tools.assert_raises(OSError, mkdirp, "")

    finally:
        shutil.rmtree(tmp)

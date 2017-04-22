#!/usr/bin/env python

# Copyright 2017 Mathew Odden
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import os
import shutil
import logging

LOG = logging.getLogger(__name__)

header = """
Copyright 2017 Mathew Odden

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


def get_header():
    commented = ''
    for line in header.split('\n')[1:-1]:
        if line:
            commented += '# %s\n' % line
        else:
            commented += '#\n'
    return commented


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('PATH', nargs='+')
    p.add_argument('--add', action='store_true')
    p.add_argument('--verbose', '-v', action='store_true')

    return p.parse_args()


def update_file(content, file_path):
    tempfile_name = "%s.i" % file_path
    try:
        with open(tempfile_name, 'w') as tempfile:

            first_line = False
            copyright_done = False
            for line in content.split('\n')[:-1]:
                if not first_line:
                    first_line = True
                    if line.startswith('#!'):
                        tempfile.write(line + '\n')
                        continue

                if not copyright_done:
                    tempfile.write('\n')
                    tempfile.writelines(get_header())
                    tempfile.write('\n')
                    copyright_done = True

                tempfile.write(line + '\n')

        LOG.debug("Copying %s to %s" % (tempfile_name, file_path))
        shutil.copy(tempfile_name, file_path)
    finally:
        try:
            os.remove(tempfile_name)
        except OSError:
            LOG.warn("No temp file found to remove?")


def main():
    args = parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    for file_path in args.PATH:
        with open(file_path, 'r+') as source_file:

            file_content = source_file.read()
            if get_header() in file_content:
                print 'Found copyright in: %s' % file_path
                continue
            else:
                print 'No copyright found in: %s' % file_path
                if args.add:
                    update_file(file_content, file_path)
                else:
                    print 'Use --add to update the file'


if __name__ == "__main__":
    main()

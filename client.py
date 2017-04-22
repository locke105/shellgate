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
import base64
import httplib
import sys
import select
import os
import fcntl
import getpass

import shellgate.tty

termst = None


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('path', type=str)
    p.add_argument('--username', '-u')
    p.add_argument('--password', '-p')
    p.add_argument('--ask-password', '-P', action='store_true',
                   help='If set, will prompt for password')

    return p.parse_args()


def main():
    args = _parse_args()

    if args.ask_password:
        password = getpass.getpass()
    else:
        password = args.password


    conn = httplib.HTTPConnection("localhost:5000")

    encoded_auth = base64.b64encode('%s:%s' % (args.username, password))

    conn.request('GET', args.path,
        headers={'Upgrade': 'tcp',
                 'Connection': 'Upgrade',
                 'Authorization': encoded_auth})

    resp = conn.getresponse()

    if resp.status != 101:
        raise Exception

    print resp.status, resp.reason
    print str(resp.msg)

    try:
        shellgate.tty.set_raw()

        stop = False

        set_nonblocking(sys.stdin)
        set_nonblocking(sys.stdout)
        set_nonblocking(sys.stderr)

        while not stop:

            #sys.stderr.write("Beginning select()\n")
            readset = [sys.stdin, conn.sock]
            readable, writable, error = select.select(readset, [], [])
            for stream in readable:
                if stream == sys.stdin:
                    #sys.stderr.write("reading stdin\n")
                    indata = sys.stdin.read()
                    #sys.stderr.write("got data %r\n" % indata)
                    if indata:
                        conn.sock.sendall(indata)
                    else:
                        # EOF
                        stop = True
                        sys.stdout.write('\n')
                        break
                else:
                    data = conn.sock.recv(4096)
                    if data:
                        sys.stdout.write(data)
                        sys.stdout.flush()
                    else:
                        # EOF
                        stop = True
                        break
    finally:
        shellgate.tty.restore_term()


def set_nonblocking(fd):
    return fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)


if __name__ == "__main__":
    main()

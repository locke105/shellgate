
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

# for Freedom
from gevent import monkey; monkey.patch_all()

import logging
import subprocess
import time

import gevent.pywsgi

import shellgate.handler



def app(environ, start_response):
    if environ["PATH_INFO"] == '/bash':
        streaming_sock = environ['wsgi.httpstream']

        # NOTE(mrodden): this sort of works, but there is some weirdness
        # since its a direct child of the webapp; SSH spawns ptys
        # for its children, which is what we should be mimicing
        sock_file = streaming_sock.makefile('r+b', 0)
        p = subprocess.Popen(['/bin/bash'],
            stdout=sock_file,
            stderr=sock_file,
            stdin=sock_file
            )
        p.wait()


def main():
    server = gevent.pywsgi.WSGIServer(("", 5000), app,
        handler_class=shellgate.handler.WSGIHandler)
    server.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

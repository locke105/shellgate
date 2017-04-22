
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

import base64
import logging
import subprocess
import select
import time

import flask
import gevent.pywsgi
import paramiko.client

import shellgate.handler


app = flask.Flask('shellgate')

@app.route("/ssh/<host>")
@app.route("/ssh/<host>/<port>")
def ssh(host, port=22):

    streaming_sock = flask.request.environ.get('wsgi.httpstream')
    if streaming_sock is None:
        flask.abort(400)

    print "Headers:"
    print flask.request.headers

    auth = flask.request.headers.get("Authorization")
    if not auth:
        flask.abort(400)

    username, password = base64.b64decode(auth).split(':')

    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())

    print "connecting to %s:%s" % (host, port)
    client.connect(host, port=int(port),
            username=username, password=password)

    shell = client.invoke_shell()
    shell.set_combine_stderr(True)

    try:
        stop = False
        while not stop:
            readset = [streaming_sock, shell]
            readable = select.select(readset, [], [])[0]
            for fd in readable:
                if fd == streaming_sock:
                    indata = streaming_sock.recv(4096)
                    if indata:
                        #print "Sending [%r] to ssh" % indata
                        shell.sendall(indata)
                    else:
                        print "EOF found"
                        stop = True
                        break
                else:
                    data = shell.recv(4096)
                    if data:
                        #print "Sending [%r] to client" % data
                        streaming_sock.sendall(data)
                    else:
                        # EOF
                        stop = True
                        break
    except socket.error:
        pass
    finally:
        shell.close()
        client.close()

    return ''


def main():
    server = gevent.pywsgi.WSGIServer(("", 5000), app,
        handler_class=shellgate.handler.WSGIHandler)
    server.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

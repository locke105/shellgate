
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

from gevent import pywsgi


class WSGIHandler(pywsgi.WSGIHandler):


    def run_application(self):

        self.result = self.do_upgrade()

        if self.environ.get('wsgi.httpstream'):
            self.write('')
            try:
                self.application(self.environ, lambda s, h, e=None: [])
            finally:
                pass
        else:
            return super(WSGIHandler, self).run_application()

    def do_upgrade(self):

        upgrade_proto = self.environ.get('HTTP_UPGRADE', '').lower()

        connnection_header = self.environ.get('HTTP_CONNECTION', '').lower()

        if not (upgrade_proto == 'tcp' and 'upgrade' in connnection_header):
            return

        if self.request_version != 'HTTP/1.1':
            self.start_response('402 Bad Request', [])

            return ['Bad protocol version']


        self.environ.update({'wsgi.httpstream': self.socket})

        headers = [
            ("Upgrade", "tcp"),
            ("Connection", "Upgrade")
        ]

        self.start_response("101 Switching Protocols", headers)

        assert not self.headers_sent

        self.provided_content_length = False
        self.response_use_chunked = False
        self.close_connection = True
        self.provided_date = True

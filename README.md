# shellgate
Python WSGI app for serving SSH or shell execution via HTTP/S

Do you like HTTP? Do you like SSH? Me too.

Taking some inspiration from kubernetes 'kubectl exec' and Docker's exec command,
I decided it would be neat if I had something that could replicate the functionality
but in Python. (I am not cool enough for golang yet :/ )

shellgate is both a proof of concept of how to integrate a TCP downgrade into
the Python WSGI framework and also an implementation that uses this to
get you SSH sessions via an HTTP interface. Essentially, a webservice that can
negotiate SSH sessions on the backend and serve them on the frontend.

# WSGI TCP "Upgrade"

If you are interested in the inner workings please see [handler.py](shellgate/handler.py)

# SSH HTTP webservice

The server is at [shellgate/server.py](shellgate/server.py) and the client is [client.py](client.py)

Simply run the server with `python shellgate/server.py`

The client can be used similarly, `python client.py`

See the usage for details: `python client.py --help`

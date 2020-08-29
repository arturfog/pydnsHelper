#!/bin/bash
sleep 5
curl 'http://localhost:8000/webui/start_ttl' > /dev/null
curl 'http://localhost:8000/webui/start_server' > /dev/null
exit 0

#!/bin/bash
sleep 15
curl 'http://localhost:8000/webui/start_ttl' > /dev/null
sleep 5
curl 'http://localhost:8000/webui/start_server' > /dev/null
exit 0

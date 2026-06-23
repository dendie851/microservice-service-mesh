#!/bin/sh

MESSAGE=$1
CONTENT_LENGTH=$(echo -n "$MESSAGE" | wc -c)

RESPONSE="HTTP/1.1 200 OK\r\nContent-Length: $CONTENT_LENGTH\r\nConnection: keep-alive\r\n\r\n$MESSAGE"

echo -e "$RESPONSE" > /tmp/response.txt

# socat menangani multiple concurrent connections
socat TCP-LISTEN:3000,reuseaddr,fork SYSTEM:"cat /tmp/response.txt"
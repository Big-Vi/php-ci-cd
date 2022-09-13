#!/bin/bash

REDIS_URL=$1

[ "$REDIS_URL" ] && ESCAPED_REDIS_URL=$(printf '%s\n' "$REDIS_URL" | sed -e 's/[\/&]/\\&/g')

sed -i.bak "s/session\.save_handler.*/session.save_handler = redis/; s/\;session\.save_path.*/session.save_path = $ESCAPED_REDIS_URL/" /etc/php/7.4/apache2/php.ini
#!/bin/bash
set -x

function check_service() {
    systemctl is-active --quiet $1
    STATUS=$?
    if [[ $STATUS -ne 0 ]]; then
        echo "$1 Service is getting started..."
        service $1 start
    fi
}

REDIS_URL=$1

if [[ ! -z $REDIS_URL ]]; then

[ "$REDIS_URL" ] && ESCAPED_REDIS_URL=$(printf '%s\n' "$REDIS_URL" | sed -e 's/[\/&]/\\&/g')

sed -i.bak "s/session\.save_handler.*/session.save_handler = redis/; s/\;session\.save_path.*/session.save_path = $ESCAPED_REDIS_URL/" /etc/php/7.4/apache2/php.ini

fi

if [[ $2 = "True" ]]; then

    crontab /var/www/html/cron.txt

    /var/www/html/vendor/silverstripe/framework/sake dev/build

    check_service "cron"

    ## Since running command in PHP CLI doesn't read Host level env, env is set system wide.
    declare -a envs=(
        "SS_DATABASE_SERVER" "SS_DATABASE_USERNAME" "SS_DATABASE_PASSWORD" "SS_DATABASE_NAME" 
        "ALGOLIA_ADMIN_API_KEY" "ALGOLIA_SEARCH_API_KEY" "ALGOLIA_SEARCH_APP_ID" "ALGOLIA_INDEX_NAME"
        "ALGOLIA_PREFIX_INDEX_NAME" 
    )

    ## now loop through the above array
    for env in "${envs[@]}"
    do
        echo "$env=$(printenv $env)" >> /etc/environment
    done

fi

/usr/sbin/syslog-ng --no-caps

/usr/sbin/apache2ctl -D FOREGROUND 

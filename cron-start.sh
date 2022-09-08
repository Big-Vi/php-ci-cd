#!/bin/bash

crontab /var/www/html/cron.txt

/var/www/html/vendor/silverstripe/framework/sake dev/build

cron -f
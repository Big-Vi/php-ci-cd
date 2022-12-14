ARG env=test

FROM node:14-bullseye as frontend
COPY . /var/www/html
RUN chown www-data:www-data /var/www/html/public/assets
WORKDIR /var/www/html/themes/base
COPY /themes/base/package.json /themes/base/yarn.lock ./
# RUN apt update && apt install -y python2
# RUN echo "export PYTHON=/usr/bin/python2" >> ~/.bashrc && /bin/bash -c "source ~/.bashrc" 
# RUN yarn install && yarn build
RUN rm -rf node_modules/ && rm -rf /var/lib/apt/lists/*


FROM composer:2.1.11 as vendor

COPY composer.json composer.json
COPY composer.lock composer.lock
COPY ./public ./public

RUN composer install \
    --ignore-platform-reqs \
    --no-interaction
    # --no-plugins \
    # --no-scripts \
    # --prefer-dist 


FROM ubuntu:jammy
ARG env

# CMD ["/sbin/my_init"]

# Update
RUN apt-get -q update && apt-get -qy upgrade && apt-get -qy autoremove && apt-get clean && rm -r /var/lib/apt/lists/*

# Installations
ENV TZ=Pacific/Auckland
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:ondrej/php -y \
    && apt install cron \
    && apt install -y apache2 libapache2-mod-php7.4 \
    php7.4 php7.4-bcmath php7.4-mysql php7.4-intl php7.4-json php7.4-gd php7.4-soap php7.4-tidy php7.4-zip \
    php7.4-gmp php7.4-opcache php7.4-curl php7.4-simplexml php7.4-mbstring php7.4-redis

# Apache / PHP configuration
ENV DOCUMENT_ROOT /var/www/html
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
RUN rm /var/www/html/index.html
RUN a2enmod rewrite ssl
RUN sed -i 's/upload_max_filesize.*/upload_max_filesize = 8M/; s/memory_limit.*/memory_limit = 192M/' /etc/php/7.4/apache2/php.ini

COPY apache2-foreground /usr/local/bin/

EXPOSE 80

# RUN mkdir /etc/service/apache2
# ADD apache2-foreground /etc/service/apache2/run
# RUN chmod +x /etc/service/apache2/run

COPY --from=frontend /var/www/html /var/www/html
COPY --from=vendor /app/vendor/ /var/www/html/vendor/ 
COPY --from=vendor /app/public/ /var/www/html/public/

RUN chmod 0755 /var/www/html/init.sh

ENV DOCUMENT_ROOT /var/www/html/public
# RUN REDIS_URL=$(grep 'REDIS_URL' /var/www/html/.env | cut -d'=' -f2); [ "$REDIS_URL" ] && ESCAPED_REDIS_URL=$(printf '%s\n' "$REDIS_URL" | sed -e 's/[\/&]/\\&/g') &&\
#     sed -i "s/session\.save_handler.*/session.save_handler = redis/; s/\;session\.save_path.*/session.save_path = $ESCAPED_REDIS_URL/" /etc/php/7.4/apache2/php.ini || echo REDIS not configured
CMD ["bash","-c","/usr/sbin/apache2ctl -D FOREGROUND"]
# ENTRYPOINT ["/var/www/html/init.sh"]
# CMD ["clusterName.xxxxxx.cfg.usw2.cache.amazonaws.com:port", "False"]

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
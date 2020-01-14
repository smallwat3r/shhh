# -*- coding: utf-8 -*-
# File     : Dockerfile
# Date     : 12.01.2020
# Author   : Matthieu Petiteau <mpetiteau.pro@gmail.com>

FROM nginx:1.17.7-alpine

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/

RUN rm /etc/nginx/conf.d/default.conf
COPY ./conf.d/shhh.conf /etc/nginx/conf.d/

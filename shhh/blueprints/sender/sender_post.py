#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : sender_post.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Sender routes."""
from datetime import datetime, timedelta

from flask import jsonify, redirect, render_template, request, url_for

from . import DIR_PATH, sender
from ... import utils

from htmlmin.minify import html_minify as mn


@sender.route('/create')
def create():
    """Create a secret."""
    return mn(render_template('create.html'))


@sender.route('/api/send', methods=['POST'])
def generate_link():
    """Generate link to access secret."""
    secret = request.form.get('inputSecret')
    passphrase = request.form.get('passPhrase')
    expires = request.form.get('expiresValue')

    if not secret or not passphrase or not expires:
        return redirect(url_for('sender.create'))

    link = utils.generate_random_slug()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with utils.DbConn(DIR_PATH) as db:
        db.commit('store_encrypt.sql', {
            'slug_link': link,
            'passphrase': utils.encrypt_passphrase(passphrase),
            'encrypted_text': utils.encrypt_message(
                secret.encode(), passphrase),
            'date_created': now,
            'date_expires': (datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                             + timedelta(days=int(expires)))
        })

    return jsonify({'slug': link, 'expires': expires})

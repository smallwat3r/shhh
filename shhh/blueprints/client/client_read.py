#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : client_read.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 17.09.2019

"""Client (reader) routes."""
import html

from flask import jsonify, render_template, request

from . import client, DIR_PATH
from ... import utils

from htmlmin.minify import html_minify as mn


@client.route('/read')
def read():
    """Read a secret."""
    slug = request.args.get('slug')

    if not slug:
        return mn(render_template('not_found.html'))

    return mn(render_template('read.html'))


@client.route('/api/read', methods=['POST'])
def decrypt():
    """Decrypt message from slug."""
    slug = request.args.get('slug')
    passphrase = request.form.get('passPhrase')

    with utils.DbConn(DIR_PATH) as db:
        encrypted = db.get('retrieve_from_slug.sql', {
            'slug': slug
        })

    if not encrypted:
        return jsonify({'status': 'error',
                        'msg': 'Sorry the data has expired'})

    if not utils.validate_passphrase(passphrase, encrypted[0]['passphrase']):
        return jsonify({'status': 'error',
                        'msg': 'Sorry the passphrase is not valid'})

    msg = html.escape(utils.decrypt_message(
        encrypted[0]['encrypted_text'], passphrase))

    return jsonify({'status': 'success',
                    'msg': '<br />'.join(msg.split('\n'))})

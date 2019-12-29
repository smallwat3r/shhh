#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : views.py
# Date  : 17.09.2019
# Author: matthieu petiteau <mpetiteau.pro@gmail.com>

'''Flask views.'''
import ast

from flask import (redirect, render_template, request, send_from_directory,
                   url_for)

from . import app, utils
from .decorators import check_arg, on_post


@app.route('/')
def index():
    return redirect(url_for('create'))


@app.route('/c', methods=['GET', 'POST'])
@check_arg('data')
def create():
    '''Create a secret.'''

    @on_post(('inputSecret', 'passPhrase', 'expiresValue',))
    def _generate():
        data = utils.generate_link(
            secret=request.form.get('inputSecret'),
            passphrase=request.form.get('passPhrase'),
            expires=request.form.get('expiresValue')
        )
        data['url'] = request.url_root
        return data

    def _data():
        if request.args.get('data'):
            return ast.literal_eval(request.args.get('data'))

    if request.method == 'POST':
        return redirect(url_for('create', data=_generate()))

    return render_template('create.html', data=_data())


@app.route('/r/<slug>', methods=['GET', 'POST'])
def read(slug):
    '''Read a secret.'''

    def _decrypt():
        return utils.decrypt(
            slug=slug,
            passphrase=request.form.get('passPhrase')
        )

    if request.method == 'POST':
        return redirect(f"read/{slug}?data={_decrypt}")

    return render_template('read.html', data=None)


@app.errorhandler(404)
def error_404(error):
    '''404 not found.'''
    return render_template('404.html')


@app.route('/robots.txt')
def static_from_root():
    '''Robots.txt'''
    return send_from_directory(app.static_folder, request.path[1:])

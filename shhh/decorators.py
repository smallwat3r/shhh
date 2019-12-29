#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : decorators.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 29.12.2019

'''Custom decorators.'''
import ast

from functools import wraps

from flask import redirect, request, url_for


def on_post(arguments):
    '''Handles POST request with mandatory args.'''
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            for arg in arguments:
                if not request.form.get(arg):
                    return redirect(url_for('create'))
            return f(*args, **kwargs)
        return wrapper
    return inner


def check_arg(arg):
    '''Check GET arg is valid.'''
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.args.get('data'):
                try:
                    data = ast.literal_eval(request.args.get('data'))
                except ValueError:
                    return redirect(url_for('create'))
                if not data.get('slug') or not data.get('expires'):
                    return redirect(url_for('create'))
            return f(*args, **kwargs)
        return wrapper
    return inner

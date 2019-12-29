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
    '''Check POST request got all mandatory args.'''
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            for arg in arguments:
                if not request.form.get(arg):
                    return redirect(url_for('create'))
            return f(*args, **kwargs)
        return wrapper
    return inner


def need_arg(arguments):
    '''Check if all args are in the GET request.'''
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            for arg in arguments:
                if not request.args.get(arg):
                    return redirect(url_for('error_404'))
            return f(*args, **kwargs)
        return wrapper
    return inner


def check_arg(arg):
    '''Check if GET data arg is a valid JSON model.'''
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.args.get('data'):
                try:
                    data = ast.literal_eval(request.args.get('data'))
                except ValueError:
                    return redirect(url_for('create'))
                if not data.get('l') or not data.get('e'):
                    return redirect(url_for('create'))
            return f(*args, **kwargs)
        return wrapper
    return inner

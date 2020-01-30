#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : decorators.py
# Author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
# Date  : 29.12.2019

"""Custom decorators."""
from functools import wraps
from flask import redirect, request


def mandatory(arguments):
    """Check if all args are in the request after redirect."""

    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            for arg in arguments:
                if not request.args.get(arg):
                    return redirect("/")
            return f(*args, **kwargs)

        return wrapper

    return inner

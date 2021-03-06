# -*- coding: utf-8 -*-
''' This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/. '''

from functools import wraps
from flask import current_app, flash, redirect, url_for
from flask_login import current_user

import app.database as data
from app.middleware import db


def is_god():
    ''' Check if the current user is God! '''
    with current_app.app_context():
        return getattr(current_user, 'role_id', None) == 1


def is_admin():
    ''' Check if the current user is of the Administrator role. '''
    with current_app.app_context():
        return getattr(current_user, 'role_id', None) == 1


def is_operator():
    ''' Check if the current user is of the Operator role. '''
    with current_app.app_context():
        return getattr(current_user, 'role_id', None) == 3


def has_offices():
    ''' Check if there's any offices created yet. '''
    with current_app.app_context():
        return data.Office.query.first() is not None


def is_office_operator(office_id):
    ''' Check if the current user's an office operator.

    Parameters
    ----------
        office_id: int
            id of the office to check for its operators.

    Returns
    -------
        True if a valid operator False if not
    '''
    operator = data.Operators.get(current_user.id)

    return bool(operator and operator.office_id == office_id)


def is_common_task_operator(task_id):
    ''' Check if the current user's an operator of common task.

    Parameters
    ----------
        task_id: int
            common task's id to check for its operators.

    Returns
    -------
        True if a valid operator False if not
    '''
    task = data.Task.get(task_id)

    return any([
        is_office_operator(office.id) for office in (task and task.offices) or []
    ])


def reject_not_god(function):
    ''' Decorator to flash and redirect to `core.root` if current user is not God.

    Parameters
    ----------
        function: callable
            the endpoint we want to reject unGodly users to access.

    Returns
    -------
        Decorator for the passed `function`.
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        if is_god() or current_app.config.get('LOGIN_DISABLED'):
            return function(*args, **kwargs)
        with current_app.app_context():
            flash('Error: only main Admin account can access the page', 'danger')
            return redirect(url_for('core.root'))

    return decorated


def reject_god(function):
    ''' Decorator to flash and redirect to `core.root` if current user is God.

    Parameters
    ----------
        function: callable
            the endpoint we want to reject unGodly users to access.

    Returns
    -------
        Decorator for the passed `function`.
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        if not is_god():
            return function(*args, **kwargs)
        with current_app.app_context():
            flash('Error: main admin account cannot be updated .', 'danger')
            return redirect(url_for('core.root'))

    return decorated


def reject_not_admin(function):
    ''' Decorator to flash and redirect to `core.root` if current user is not administrator.

    Parameters
    ----------
        function: callable
            the endpoint we want to reject unGodly users to access.

    Returns
    -------
        Decorator for the passed `function`.
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        if is_admin() or current_app.config.get('LOGIN_DISABLED'):
            return function(*args, **kwargs)
        with current_app.app_context():
            flash('Error: only administrator can access the page', 'danger')
            return redirect(url_for('core.root'))

    return decorated


def reject_operator(function):
    ''' Decorator to flash and redirect to `core.root` if current user is operator.

    Parameters
    ----------
        function: callable
            the endpoint we want to reject unGodly users to access.

    Returns
    -------
        Decorator for the passed `function`.
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        if is_operator():
            with current_app.app_context():
                flash('Error: operators are not allowed to access the page ', 'danger')
                return redirect(url_for('core.root'))
        return function(*args, **kwargs)

    return decorated


def reject_no_offices(function):
    ''' Decorator to flash and redirect to `manage_app.all_offices`
        if there's not any offices created yet.

    Parameters
    ----------
        function: callable
            the endpoint we want to reject unGodly users to access.

    Returns
    -------
        Decorator for the passed `function`.
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        if has_offices():
            return function(*args, **kwargs)
        with current_app.app_context():
            flash('Error: No offices exist to delete', 'danger')
            return redirect(url_for('manage_app.all_offices'))

    return decorated

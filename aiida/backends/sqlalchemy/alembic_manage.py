#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
import sys

AVAIL_AL_COMMANDS = ['revision', 'current', 'history']

if __name__ == "__main__":
    # Copy sys.argv
    actual_argv = sys.argv[:]

    # Check if the first cmdline option is --aiida-process=PROCESSNAME
    try:
        first_cmdline_option = sys.argv[1]
    except IndexError:
        first_cmdline_option = None

    process_name = None  # Use the default process if not specified
    if first_cmdline_option is not None:
        cmdprefix = "--aiida-process="
        if first_cmdline_option.startswith(cmdprefix):
            process_name = first_cmdline_option[len(cmdprefix):]
            # I remove the argument I just read
            actual_argv = [sys.argv[0]] + sys.argv[2:]

    # Check if there is also a cmdline option is --aiida-profile=PROFILENAME
    try:
        first_cmdline_option = actual_argv[1]
    except IndexError:
        first_cmdline_option = None

    profile_name = None  # Use the default profile if not specified
    if first_cmdline_option is not None:
        cmdprefix = "--aiida-profile="
        if first_cmdline_option.startswith(cmdprefix):
            profile_name = first_cmdline_option[len(cmdprefix):]
            # I remove the argument I just read
            actual_argv = [actual_argv[0]] + actual_argv[2:]

    if actual_argv[1] in AVAIL_AL_COMMANDS:
        # Perform the same loading procedure as the normal load_dbenv does
        from aiida.backends import settings
        settings.LOAD_DBENV_CALLED = True
        # We load the needed profile.
        # This is going to set global variables in settings, including
        # settings.BACKEND
        from aiida.backends.profile import load_profile
        load_profile(process=process_name, profile=profile_name)
        from aiida.backends.profile import BACKEND_SQLA
        if settings.BACKEND != BACKEND_SQLA:
            from aiida.common.exceptions import InvalidOperation
            raise InvalidOperation("A SQLAlchemy (alembic) revision "
                                   "generation procedure is initiated "
                                   "but a different backend is used!")
        # We load the Django specific _load_dbenv_noschemacheck
        # When there will be a need for SQLAlchemy for a schema migration,
        # we may abstract thw _load_dbenv_noschemacheck and make a common
        # one for both backends
        from aiida.backends.sqlalchemy.utils import _load_dbenv_noschemacheck
        _load_dbenv_noschemacheck(process=process_name, profile=profile_name)

        from aiida.backends.sqlalchemy.utils import alembic_command
        if actual_argv[1] == 'revision':
            alembic_command(actual_argv[1], autogenerate=True,
                            message="Added account table")
        if actual_argv[1] == 'current':
            alembic_command(actual_argv[1])
        if actual_argv[1] == 'history':
            alembic_command(actual_argv[1])
    else:
        print("No valid command specified. The available commands are: ")

# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################

from aiida.orm.implementation.calculation import Calculation
from aiida.common.lang import override
from aiida.common import caching

class WorkCalculation(Calculation):
    """
    Used to represent a calculation generated by a Process from the new
    workflows system.
    """
    FINISHED_KEY = '_finished'
    FAILED_KEY = '_failed'
    _hash_ignored_attributes = [FINISHED_KEY]

    _hash_ignored_inputs = ['_return_pid', '_fast_forward']
    _hash_ignored_attributes = ['_finished', '_sealed']

    @override
    def has_finished_ok(self):
        """
        Returns True if the work calculation finished normally, False otherwise
        (could be that it's still running)

        :return: True if finished successfully, False otherwise.
        :rtype: bool
        """
        return self.get_attr(self.FINISHED_KEY, False)

    @override
    def has_failed(self):
        """
        Returns True if the work calculation failed because of an exception,
        False otherwise

        :return: True if the calculation has failed, False otherwise.
        :rtype: bool
        """
        return self.get_attr(self.FAILED_KEY, False) is not False

    def get_hash(self):
        from aiida.common.hashing import make_hash
        base_hash = super(WorkCalculation, self).get_hash()
        if base_hash is None:
            return None
        try:
            return make_hash([
                base_hash,
                {
                    key: value.get_hash() for key, value in self.get_inputs_dict().items()
                    if key not in self._hash_ignored_inputs
                }
            ])
        except:
            return None

    def _is_valid_cache(self):
        return super(WorkCalculation, self)._is_valid_cache() and self.has_finished_ok

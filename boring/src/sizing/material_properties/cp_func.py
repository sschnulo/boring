"""
These helper functions are a placeholder until a derivative friendly method replaces it (akima, convolution)


Apparent Heat Capacity Method
# https://link.springer.com/article/10.1007/s10973-019-08541-w

Author: Jeff Chin
"""
from __future__ import absolute_import

import openmdao.api as om
import numpy as np


class PCM_Cp(om.ExplicitComponent):

    def initialize(self):
        self.options.declare('num_nodes', types=int)  # parallel execution

    def setup(self):
        nn = self.options['num_nodes']

        # pad geometry
        self.add_input('T', 280 * np.ones(nn), units='K', desc='PCM temp')
        self.add_input('T_lo', 333 * np.ones(nn), units='K', desc='PCM lower temp transition point')
        self.add_input('T_hi', 338 * np.ones(nn), units='K', desc='PCM upper temp transition point')

        # outputs
        self.add_output('cp_pcm', 1.54 * np.ones(nn), units='kJ/(kg*K)', desc='specific heat of the pcm')

    def setup_partials(self):
        # self.declare_partials('*', '*', method='cs')
        nn = self.options['num_nodes']
        ar = np.arange(nn)

        self.declare_partials('cp_pcm', ['T', 'T_lo', 'T_hi'], rows=ar, cols=ar)

    def compute(self, inputs, outputs):

        outputs['cp_pcm'] = cp_basic(T = inputs['T'], T1 = inputs['T_lo'], T2 = inputs['T_hi'])

    def compute_partials(self, inputs, partials):
        T = inputs['T']

        partials['cp_pcm', 'T'] = cp_dT_deriv_func(T)
        partials['cp_pcm', 'T_lo'] = cp_dT_deriv_func(T)
        partials['cp_pcm', 'T_hi'] = cp_dT_deriv_func(T)


def cp_basic(T, T1=60 + 273, T2=65 + 273, Cp_low=1.5, Cp_high=50):  # kJ/kgK
    Cp = np.empty_like(T)
    
    T_cp_hi = np.logical_and(T1 < T, T < T2)
    T_cp_low = np.logical_not(T_cp_hi)

    Cp[T_cp_hi] = Cp_high
    Cp[T_cp_low] = Cp_low

    return Cp


def cp_dT_deriv_func(T):
    return 0

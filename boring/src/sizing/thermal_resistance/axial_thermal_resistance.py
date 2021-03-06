from __future__ import absolute_import
import numpy as np
from math import pi

import openmdao.api as om
import numpy as np


class AxialThermalResistance(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)

    def setup(self):
        nn=self.options['num_nodes']

        self.add_input('epsilon', 0.46*np.ones(nn), desc='wick porosity')
        self.add_input('k_w', 11.4*np.ones(nn), units='W/(m*K)', desc='copper conductivity')
        self.add_input('k_l', 3*np.ones(nn), units='W/(m*K)', desc='liquid conductivity')
        self.add_input('L_eff', 4*np.ones(nn), units='m', desc='Effective Length') # Effective, not Adiabatic!
        self.add_input('A_w', 5*np.ones(nn), units='m**2', desc='Wall Area')
        self.add_input('A_wk', 6*np.ones(nn), units='m**2', desc='Wick Area')

        self.add_output('k_wk', val=1.0*np.ones(nn), units='W/(m*K)', desc='Wick Conductivity')
        self.add_output('R_aw', val=1.0*np.ones(nn), units='K/W', desc='Wall Axial Resistance')
        self.add_output('R_awk', val=1.0*np.ones(nn), units='K/W', desc='Wick Axial Resistance')

    def setup_partials(self):
        nn=self.options['num_nodes']
        ar = np.arange(nn) 

        self.declare_partials('k_wk', ['epsilon', 'k_w', 'k_l'], rows=ar, cols=ar)
        self.declare_partials('R_aw', ['L_eff', 'A_w', 'k_w'], rows=ar, cols=ar)
        self.declare_partials('R_awk', ['L_eff', 'A_wk', 'epsilon', 'k_w', 'k_l'], rows=ar, cols=ar)

    def compute(self, inputs, outputs):

        epsilon = inputs['epsilon']
        k_w = inputs['k_w']
        k_l = inputs['k_l']
        L_eff = inputs['L_eff']
        A_w = inputs['A_w']
        k_w = inputs['k_w']
        A_wk = inputs['A_wk']

        outputs['k_wk']=(1-epsilon)*k_w+epsilon*k_l
        outputs['R_aw']=L_eff/(A_w*k_w)
        outputs['R_awk']=L_eff/(A_wk*outputs['k_wk'])

    def compute_partials(self, inputs, J):

        epsilon = inputs['epsilon']
        k_w = inputs['k_w']
        k_l = inputs['k_l']
        L_eff = inputs['L_eff']
        A_w = inputs['A_w']
        k_w = inputs['k_w']
        A_wk = inputs['A_wk']

        d_k_wk__d_epsilon = -k_w + k_l

        J['k_wk', 'epsilon'] = -k_w + k_l
        J['k_wk', 'k_w'] = (1 - epsilon)
        J['k_wk', 'k_l'] = epsilon

        J['R_aw', 'L_eff'] = 1/(A_w*k_w) 
        J['R_aw', 'A_w'] = -L_eff/(A_w**2*k_w)
        J['R_aw', 'k_w'] = -L_eff/(A_w*k_w**2)

        J['R_awk', 'L_eff'] = 1/(A_wk*((1-epsilon)*k_w+epsilon*k_l))
        J['R_awk', 'A_wk'] = -L_eff/(A_wk**2*((1-epsilon)*k_w+epsilon*k_l))
        J['R_awk', 'epsilon'] = -L_eff/(A_wk*((1-epsilon)*k_w+epsilon*k_l)**2) * (-k_w + k_l)
        J['R_awk', 'k_w'] = -L_eff/(A_wk*((1-epsilon)*k_w+epsilon*k_l)**2) * (1-epsilon)
        J['R_awk', 'k_l'] = -L_eff/(A_wk*((1-epsilon)*k_w+epsilon*k_l)**2) * epsilon


# # ------------ Derivative Checks --------------- #
if __name__ == '__main__':
    from openmdao.api import Problem

    nn = 1

    prob = Problem()
    prob.model.add_subsystem('comp1', AxialThermalResistance(num_nodes=nn), promotes_outputs=['*'], promotes_inputs=['*'])
    prob.setup(force_alloc_complex=True)
    prob.run_model()
    prob.check_partials(method='cs', compact_print=True)

    print('k_wk = ', prob.get_val('comp1.k_wk'))
    print('R_aw = ', prob.get_val('comp1.R_aw'))
    print('R_awk = ', prob.get_val('comp1.R_awk'))
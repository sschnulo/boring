"""
Run a heat pipe transient, where the final temperature of the condensor is specified,
dymos will determine the duration of the simulation

Authors: Sydney Schnulo, Jeff Chin
"""

import openmdao.api as om

import numpy as np
import dymos as dm

from boring.src.sizing.heatpipe_run import HeatPipeRun  # import the ODE
from boring.util.save_csv import save_csv

from boring.util.load_inputs import load_inputs


def hp_transient(transcription='gauss-lobatto', num_segments=5,
                 transcription_order=3, compressed=False, optimizer='SLSQP',
                 run_driver=True, force_alloc_complex=True, solve_segments=False,
                 show_plots=False, save=True, Tf_final=370):
    p = om.Problem(model=om.Group())
    model = p.model
    nn = 1
    p.driver = om.ScipyOptimizeDriver()
    p.driver = om.pyOptSparseDriver(optimizer=optimizer)

    p.driver.declare_coloring()

    traj = p.model.add_subsystem('traj', dm.Trajectory())

    phase = traj.add_phase('phase',
                           dm.Phase(ode_class=HeatPipeRun,
                                    transcription=dm.GaussLobatto(num_segments=num_segments, order=transcription_order,
                                                                  compressed=compressed)))

    phase.set_time_options(fix_initial=True, fix_duration=False, duration_bounds=(1., 3200.))

    phase.add_state('T_cond', rate_source='cond.Tdot', targets='cond.T', units='K',  # ref=333.15, defect_ref=333.15,
                    fix_initial=True, fix_final=False, solve_segments=solve_segments)
    phase.add_state('T_cond2', rate_source='cond2.Tdot', targets='cond2.T', units='K',  # ref=333.15, defect_ref=333.15,
                    fix_initial=True, fix_final=False, solve_segments=solve_segments)

    phase.add_control('T_evap', targets='evap.Rex.T_in', units='K',
                      opt=False)

    phase.add_boundary_constraint('T_cond', loc='final', equals=Tf_final)

    phase.add_objective('time', loc='final', ref=1)

    phase.add_timeseries_output('evap_bridge.Rv.q', output_name='eRvq', units='W')
    phase.add_timeseries_output('evap_bridge.Rwa.q', output_name='eRwaq', units='W')
    phase.add_timeseries_output('evap_bridge.Rwka.q', output_name='eRwkq', units='W')
    phase.add_timeseries_output('cond_bridge.Rv.q', output_name='cRvq', units='W')
    phase.add_timeseries_output('cond_bridge.Rwa.q', output_name='cRwaq', units='W')
    phase.add_timeseries_output('cond_bridge.Rwka.q', output_name='cRwkq', units='W')
    phase.add_timeseries_output('evap.pcm.PS', output_name='ePS', units=None)
    phase.add_timeseries_output('cond.pcm.PS', output_name='cPS', units=None)
    phase.add_timeseries_output('cond2.pcm.PS', output_name='c2PS', units=None)

    p.model.linear_solver = om.DirectSolver()
    p.setup(force_alloc_complex=force_alloc_complex)

    p['traj.phase.t_initial'] = 0.0
    p['traj.phase.t_duration'] = 195.
    p['traj.phase.states:T_cond'] = phase.interpolate(ys=[293.15, 333.15], nodes='state_input')
    p['traj.phase.states:T_cond2'] = phase.interpolate(ys=[293.15, 333.15], nodes='state_input')
    p['traj.phase.controls:T_evap'] = phase.interpolate(ys=[333., 338.], nodes='control_input')

    p.run_model()

    opt = p.run_driver()
    # sim = traj.simulate(times_per_seg=10)

    print('********************************')

    # save_csv(p, sim, '../../output/output.csv',
    #          y_name=['parameters:T_evap', 'states:T_cond', 'states:T_cond2',
    #                  'eRvq', 'eRwaq', 'eRwkq', 'cRvq', 'cRwaq', 'cRwkq'],
    #          y_units=['K', 'K', 'K', 'W', 'W', 'W', 'W', 'W', 'W'])

    if show_plots:
        import matplotlib.pyplot as plt

        # time = sim.get_val('traj.phase.timeseries.time', units='s')
        time_opt = p.get_val('traj.phase.timeseries.time', units='s')
        # T_cond = sim.get_val('traj.phase.timeseries.states:T_cond', units='K')
        T_cond_opt = p.get_val('traj.phase.timeseries.states:T_cond', units='K')
        # T_cond2 = sim.get_val('traj.phase.timeseries.states:T_cond2', units='K')
        T_cond2_opt = p.get_val('traj.phase.timeseries.states:T_cond2', units='K')
        # T_evap = sim.get_val('traj.phase.timeseries.controls:T_evap', units='K')
        T_evap_opt = p.get_val('traj.phase.timeseries.controls:T_evap', units='K')

        ePS_opt = p.get_val('traj.phase.timeseries.ePS')
        cPS_opt = p.get_val('traj.phase.timeseries.cPS')
        c2PS_opt = p.get_val('traj.phase.timeseries.c2PS')

        plt.plot(time_opt, T_cond_opt)
        # plt.plot(time, T_cond)

        plt.plot(time_opt, T_cond2_opt)
        # plt.plot(time, T_cond2)

        plt.plot(time_opt, T_evap_opt)
        # plt.plot(time, T_evap)

        plt.xlabel('time, s')
        plt.ylabel('T_cond, K')

        plt.show()

        plt.plot(time_opt, cPS_opt)
        # plt.plot(time, EPS)

        plt.plot(time_opt, c2PS_opt)
        # plt.plot(time, T_cond2)

        plt.plot(time_opt, ePS_opt)
        # plt.plot(time, T_evap)

        plt.xlabel('time, s')
        plt.ylabel('percent solid')

        plt.show()



    return p


if __name__ == '__main__':
    import time

    start = time.time()

    p = hp_transient(transcription='gauss-lobatto', num_segments=10,
                     transcription_order=3, compressed=False, optimizer='SNOPT',
                     run_driver=True, force_alloc_complex=True, solve_segments=False,
                     show_plots=True, Tf_final=370)
    end = time.time()

    print("elapsed time:", end - start)

#!/usr/bin/env python
''' VIC exact restart testing '''

import numpy as np
import datetime
import os
import glob
import xarray as xr
from test_utils import *

# -------------------------------------------------------------------- #
def prepare_restart_run_periods(restart_dict, state_basedir, statesec):
    ''' For restart tests, read full running period and splitting dates into datetime objects
    Parameters
    ----------
    restart_dict: <class 'configobj.Section'>
        A section of the config file for exact restart test setup
    state_basedir: <str>
        Basedirectory of output state files.
        For restart tests, state files will be output as <state_basedir>/<run_start_date>_<run_end_date>/<state_file>
    statesec: <int>
        STATESEC option in global parameter file

    Returns
    ----------
    run_periods: OrderedDict
        A list of running periods, including the full-period run, and all splitted
        runs in order. Each element of run_period is a dictionary with keys:
            start_date
            end_date
            init_state  # None, or full path of the initial state file
                        # e.g., '/path/19490101_19490105/states_19490105_82800'

    '''

    #--- Read in full running period ---#
    start_date = datetime.datetime(restart_dict['start_date'][0],
                                   restart_dict['start_date'][1],
                                   restart_dict['start_date'][2])
    end_date = datetime.datetime(restart_dict['end_date'][0],
                                 restart_dict['end_date'][1],
                                 restart_dict['end_date'][2])
    #--- Identify each of the splitted running period ---#
    list_split_dates = []
    for i, split in enumerate(restart_dict['split_dates']):
        list_split_dates.append(datetime.datetime(restart_dict['split_dates'][split][0],
                                                  restart_dict['split_dates'][split][1],
                                                  restart_dict['split_dates'][split][2]))
    #--- Prepare running periods ---#
    # run_periods is a list of running periods, including the full-period run,
    # and all splitted runs in order. Each element of run_period is a dictionary
    # with keys:
    #       start_date
    #       end_date
    #       init_state  # None, or full path of the initial state file
    #                   # e.g., '/path/19490101_19490105/states_19490105_82800'
    run_periods = []
    # Append the full run
    d = dict(start_date=start_date, end_date=end_date)
    d['init_state'] = None
    run_periods.append(d)
    # First splitted running period - start_date to first split date
    d = dict(start_date=start_date, end_date=list_split_dates[0])
    d['init_state'] = None
    run_periods.append(d)
    # Loop over each of the rest splitted periods
    for i in range(len(list_split_dates)-1):
        d = dict(start_date=list_split_dates[i] + dt.timedelta(days=1),
                 end_date=list_split_dates[i+1])
        d['init_state'] = os.path.join(
                state_basedir,
                '{}_{}'.format(run_periods[-1]['start_date'].strftime("%Y%m%d"),
                               run_periods[-1]['end_date'].strftime("%Y%m%d")),
                '{}{}_{}'.format('states_',
                                 run_periods[-1]['end_date'].strftime("%Y%m%d"),
                                 statesec))
    run_periods.append(d)
    # Last splitted running period - last split date to end_date
    d = dict(start_date=list_split_dates[len(list_split_dates)-1] +
                        datetime.timedelta(days=1),
             end_date=end_date)
    d['init_state'] = os.path.join(
            state_basedir,
            '{}_{}'.format(run_periods[-1]['start_date'].strftime("%Y%m%d"),
                           run_periods[-1]['end_date'].strftime("%Y%m%d")),
            '{}{}_{}'.format('states_',
                             run_periods[-1]['end_date'].strftime("%Y%m%d"),
                             statesec))
    run_periods.append(d)

    return run_periods
# -------------------------------------------------------------------- #

# -------------------------------------------------------------------- #
def setup_subdirs_restart_test(result_basedir, state_basedir, run_periods):
    ''' Set up subdirectories for multiple runs for restart testing
    Parameters
    ----------
    result_basedir: <str>
        Base directory of output fluxes results; running periods are subdirectories under the base directory
    state_basedir: <str>
        Base directory of output state results; running periods are subdirectories under the base directory
    run_periods: <list>
        A list of running periods. Return from prepare_restart_run_periods()

    Returns
    ----------
    None
    '''

    for j, run_period in enumerate(run_periods):
        # Set up subdirectories for results and states
        run_start_date = run_period['start_date']
        run_end_date = run_period['end_date']
        result_dir = os.path.join(result_basedir,
                                  '{}_{}'.format(run_start_date.strftime("%Y%m%d"),
                                                 run_end_date.strftime("%Y%m%d")))
        state_dir = os.path.join(state_basedir,
                                 '{}_{}'.format(run_start_date.strftime("%Y%m%d"),
                                                run_end_date.strftime("%Y%m%d")))
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(state_dir, exist_ok=True)

# -------------------------------------------------------------------- #

# -------------------------------------------------------------------- #
def setup_subdirs_and_fill_in_global_param_restart_test(s, run_periods, driver, result_basedir, state_basedir, test_data_dir, test_dir):
    ''' Fill in global parameter options for multiple runs for restart testing

    Parameters
    ----------
    s: <string.Template>
        Template of the global param file to be filled in
    run_periods: <list>
        A list of running periods. Return from prepare_restart_run_periods()
    driver: <str>
        'classic' or 'image'
    result_basedir: <str>
        Base directory of output fluxes results; running periods are subdirectories under the base directory
    state_basedir: <str>
        Base directory of output state results; running periods are subdirectories under the base directory
    test_data_dir: <str>
        Base directory of test data
    test_dir: <str>
        Directory of the testing scripts

    Returns
    ----------
    '''

    list_global_param = []
    for j, run_period in enumerate(run_periods):
        # Set up subdirectories for results and states
        run_start_date = run_period['start_date']
        run_end_date = run_period['end_date']
        result_dir = os.path.join(result_basedir,
                                  '{}_{}'.format(run_start_date.strftime("%Y%m%d"),
                                                 run_end_date.strftime("%Y%m%d")))
        state_dir = os.path.join(state_basedir,
                                 '{}_{}'.format(run_start_date.strftime("%Y%m%d"),
                                                run_end_date.strftime("%Y%m%d")))
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(state_dir, exist_ok=True)
        # Determine initial state
        if run_period['init_state']==None: # if no initial state
            init_state='#INIT_STATE'
        else: # else, the initial state is the last time step
            init_state='INIT_STATE {}'.format(run_period['init_state'])
            if driver=='image': # In image driver, the name of
                                # the state file is 'basepath.*'
                                # instead of 'basepath_*', and
                                # ends with ".nc"
                init_state = init_state.replace("states_", "states.") + '.nc'

        # Fill in global parameter options
        list_global_param.append(s.safe_substitute(
                test_dir=test_dir,
                test_data_dir=test_data_dir,
                result_dir=result_dir,
                state_dir=state_dir,
                startyear=run_start_date.year,
                startmonth=run_start_date.month,
                startday=run_start_date.day,
                endyear=run_end_date.year,
                endmonth=run_end_date.month,
                endday=run_end_date.day,
                init_state=init_state,
                stateyear=run_end_date.year,
                statemonth=run_end_date.month,
                stateday=run_end_date.day))
    return(list_global_param)
# -------------------------------------------------------------------- #

# -------------------------------------------------------------------- #
def check_exact_restart_fluxes(result_basedir, driver, run_periods):
    ''' Checks whether all the fluxes are the same w/ or w/o restart

    Parameters
    ----------
    result_basedir: <str>
        Base directory of output fluxes results; running periods are subdirectories under the base directory
    driver: <str>
        'classic' or 'image'
    run_periods: <list>
        A list of running periods. Return from prepare_restart_run_periods()

    Returns
    ----------
    None
    '''

    #--- Extract full run period ---#
    run_full_start_date = run_periods[0]['start_date']
    run_full_end_date = run_periods[0]['end_date']
    #--- Read full run fluxes ---#
    result_dir = os.path.join(
        result_basedir,
        '{}_{}'.format(run_full_start_date.strftime('%Y%m%d'),
                       run_full_end_date.strftime('%Y%m%d')))
    if driver=='classic':
        # Read in each of the output flux files
        dict_df_full_run = {}  # a dict of flux at each grid cell, keyed by flux basename
        for fname in glob.glob(os.path.join(result_dir, '*')):
            df = read_vic_ascii(fname, header=True)
            dict_df_full_run[os.path.basename(fname)] = df
    elif driver=='image':
        if len(glob.glob(os.path.join(result_dir, '*.nc')))>1:
            print('Warning: more than one netCDF file found under directory {}'.
                  format(result_dir))
        fname = glob.glob(os.path.join(result_dir, '*.nc'))[0]
        ds_full_run = xr.open_dataset(fname)

    #--- Loop over the result of each split run period ---#
    for i, run_period in enumerate(run_periods):
        # Skip the full run
        if i==0:
            continue
        # Extract running period
        start_date = run_period['start_date']
        end_date = run_period['end_date']
        # Loop over each of the output flux files
        result_dir = os.path.join(
            result_basedir,
            '{}_{}'.format(start_date.strftime('%Y%m%d'),
                           end_date.strftime('%Y%m%d')))
        if driver=='classic':
            for flux_basename in dict_df_full_run.keys():
                # Read in flux data
                fname = os.path.join(result_dir, flux_basename)
                df = read_vic_ascii(fname, header=True)
                # Extract the same period from the full run
                df_full_run_split_period = dict_df_full_run[flux_basename].truncate(
                                                         before=start_date,
                                                         after=end_date)
                # Compare split run fluxes with full run
                df_diff = df - df_full_run_split_period
                if np.absolute(df_diff).max().max() > pow(10, -6):
                    raise VICTestError('Restart causes inexact flux outputs '
                                       'for running period {} - {} at grid cell {}!'.
                                format(start_date.strftime('%Y%m%d'),
                                       end_date.strftime('%Y%m%d'),
                                       flux_basename))
                else:
                    continue
        elif driver=='image':
            # Read in flux data
            if len(glob.glob(os.path.join(result_dir, '*.nc')))>1:
                print('Warning: more than one netCDF file found under directory {}'.
                      format(result_dir))
            fname = glob.glob(os.path.join(result_dir, '*.nc'))[0]
            ds = xr.open_dataset(fname)
            # Extract the same period from the full run
            ds_full_run_split_period = ds_full_run.sel(time=slice(
                        start_date.strftime('%Y%m%d'),
                        end_date.strftime('%Y%m%d')))
            # Compare split run fluxes with full run
            for var in ds_full_run.data_vars:
                if np.absolute(ds[var] - ds_full_run_split_period[var]).\
                   max().values > 0.0:
                    raise VICTestError('Restart causes inexact flux outputs '
                                       '(variable {})'
                                       'for running period {} - {} at grid cell {}!'.
                                format(var, start_date.strftime('%Y%m%d'),
                                       end_date.strftime('%Y%m%d')))
                else:
                    continue
    return
# -------------------------------------------------------------------- #

# -------------------------------------------------------------------- #
def check_exact_restart_states(state_basedir, driver, run_periods, statesec, state_format='ASCII'):
    ''' Checks whether all the states are the same w/ or w/o restart.
        Only test the state at the last time step.

    Parameters
    ----------
    state_basedir: <str>
        Base directory of output state results; running periods are subdirectories under the base directory
    driver: <str>
        'classic' or 'image'
    run_periods: <list>
        A list of running periods. Return from prepare_restart_run_periods()
    statesec: <int>
        STATESEC option in global parameter file
    state_format: <str>
        state file format, 'ASCII' or 'BINARY'; only need to specify when driver=='classic'

    Returns
    ----------
    None
    '''

    #--- Read the state at the end of the full run ---#
    # Extract full run period
    run_full_start_date = run_periods[0]['start_date']
    run_full_end_date = run_periods[0]['end_date']
    # Read the state file
    if driver=='classic':
        state_fname = os.path.join(
            state_basedir,
            '{}_{}'.format(run_full_start_date.strftime('%Y%m%d'),
                           run_full_end_date.strftime('%Y%m%d')),
            'states_{}_{}'.format(run_full_end_date.strftime('%Y%m%d'),
                                  statesec))
        if state_format=='ASCII':
            states_full_run = read_ascii_state(state_fname)
        elif state_format=='BINARY':
            states_full_run = read_binary_state(state_fname)
    elif driver=='image':
        state_fname = os.path.join(
            state_basedir,
            '{}_{}'.format(run_full_start_date.strftime('%Y%m%d'),
                           run_full_end_date.strftime('%Y%m%d')),
            'states.{}_{}.nc'.format(run_full_end_date.strftime('%Y%m%d'),
                                     statesec))
        ds_states_full_run = xr.open_dataset(state_fname)

    #--- Read the state at the end of the last period of run ---#
    # Extract the last split run period
    run_last_period_start_date = run_periods[-1]['start_date']
    run_last_period_end_date = run_periods[-1]['end_date']
    # Read the state file
    if driver=='classic':
        state_fname = os.path.join(
            state_basedir,
            '{}_{}'.format(run_last_period_start_date.strftime('%Y%m%d'),
                           run_last_period_end_date.strftime('%Y%m%d')),
            'states_{}_{}'.format(run_last_period_end_date.strftime('%Y%m%d'),
                                  statesec))
        if state_format=='ASCII':
            states = read_ascii_state(state_fname)
        elif state_format=='BINARY':
            states = read_binary_state(state_fname)
    elif driver=='image':
        state_fname = os.path.join(
            state_basedir,
            '{}_{}'.format(run_last_period_start_date.strftime('%Y%m%d'),
                           run_last_period_end_date.strftime('%Y%m%d')),
            'states.{}_{}.nc'.format(run_last_period_end_date.strftime('%Y%m%d'),
                                     statesec))
        ds_states = xr.open_dataset(state_fname)

    #--- Compare split run states with full run ---#
    if driver=='classic':
        # If ASCII state file, check if almost the same
        if state_format=='ASCII':
            states_diff = states - states_full_run
            if np.absolute(states_diff).max() > pow(10, -3):
                raise VICTestError('Restart causes inexact state outputs!')
            else:
                return
        # If BINARY state file, check if exactly the same
        elif state_format=='BINARY':
            if states!=states_full_run:
                raise VICTestError('Restart causes inexact state outputs!')
            else:
                return
    elif driver=='image':
        for var in ds_states.data_vars:
            if np.absolute(ds_states[var] - ds_states_full_run[var]).\
               max().values > 0.0:
                raise VICTestError('Restart causes inexact state outputs'
                                   '(var {}) !'.format(var))
            else:
                continue
        return
# -------------------------------------------------------------------- #

# -------------------------------------------------------------------- #
def read_ascii_state(state_fname):
    ''' Read in ascii format state file and convert to a list of numbers

    Parameters
    ----------
    state_fname: <str>
        Path of the state file to be read

    Returns
    ----------
    states: <np.array>
        A np.array of float numbers of the state file
    '''

    with open(state_fname, 'r') as f:
        list_states = f.read().split()
        for i, item in enumerate(list_states):
            list_states[i] = float(item)
    return np.asarray(list_states)
# -------------------------------------------------------------------- #

# -------------------------------------------------------------------- #
def read_binary_state(state_fname):
    ''' Read in ascii format state file and convert to a list of numbers

    Parameters
    ----------
    state_fname: <str>
        Path of the state file to be read

    Returns
    ----------
    states: <bytes>
        The full binary state file content
    '''

    with open(state_fname, 'rb') as f:
        states = f.read()
    return states
# -------------------------------------------------------------------- #



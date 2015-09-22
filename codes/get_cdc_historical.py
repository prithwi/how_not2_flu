#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author : Prithwish Chakraborty <prithwi@vt.edu>,
#          Bryan Lewis  <blewis@vbi.vt.edu>
# date   : 2015-09-21
# LICENSE: MIT
"""
Code to get historical CDC data

Note: CDC doesn't update for week 52 even if its present
#TODO: see if this can be expanded to multiple regions 
"""

import pandas as pd
import numpy as np
import argparse
import sys
import logging as logs

log = logs.getLogger()

DEFAULT_OUT = './historical_cdc.csv'
BASEURL_PREFIX = "http://www.cdc.gov/flu/weekly/weeklyarchives"
BASEURL_SUFFIX = "/data/senAllregt"
DATA_COLUMNS = ['Week', 'age0to4', 'age5to24', 'age25to49', 'age50to64',
                'age64plus', 'TotalILI', 'TotalPatients', 'UnweightedILI',
                'WeightedILI']
WEEK_RANGE = np.r_[np.arange(40, 53), np.arange(1, 40)]
       

def get_seasons(seasons, sniff=True, skip_prev_season=True):
    """get historical cdc data for specified seasons

    :seasons: list of ints
    :returns: stacked df
    """
    #    INITIALIZATIONS
    CDC_hist_archive = pd.DataFrame()
    gen_cols = None 

    for season in sorted(seasons):
        # REINITIALIZING for each season
        last_dump = pd.DataFrame(columns=DATA_COLUMNS)

        for week in WEEK_RANGE:
            url = "{}{}-{}{}{:02d}.htm".format(BASEURL_PREFIX, 
                                               season - 1, season,
                                               BASEURL_SUFFIX, week)
            log.debug(u'URL used: {}'.format(url))

            if sniff:
                gen_cols = pd.read_html(url, skiprows=1)[0].columns
                if len(gen_cols) == len(DATA_COLUMNS):
                    sniff = False
                else:
                    raise Exception('Sniffing failed')

            try:
                temp = pd.read_html(url, skiprows=1)
                current_dump = temp[0]
                if gen_cols is not None:
                    current_dump = current_dump[gen_cols]

                current_dump.columns = DATA_COLUMNS
                if skip_prev_season:
                    first_season_idx = current_dump[current_dump.Week == 40].index[0]
                    current_dump = current_dump.ix[first_season_idx:, :]

            except Exception as e:
                current_dump = last_dump
                log.debug(u'Error for {} is {}'.format(url, e))

            current_dump['season'] = season
            current_dump['week_reported'] = week
            
            # updating
            CDC_hist_archive = CDC_hist_archive.append(current_dump)
            last_dump = current_dump[DATA_COLUMNS]

    CDC_hist_archive = CDC_hist_archive[['week_reported', 'season'] +
                                        DATA_COLUMNS]
    return CDC_hist_archive


def init_logs(arg, log):
    if arg and vars(arg).get('verbose', False):
        l = logs.DEBUG
    else:
        l = logs.INFO
    
    # printing to stdout
    ch = logs.StreamHandler(sys.stdout)
    formatter = logs.Formatter('%(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.setLevel(l)
    return


def parse_args():
    '''
    Reads the command line options and parses the appropriate commands
    '''
    ap = argparse.ArgumentParser('Historical CDC archive downloader')
    # Main options
    ap.add_argument("-s", "--seasons", metavar='SEASONS', required=True,
                    nargs='+', type=int,
                    help="seasons to download data for.")
    ap.add_argument("-o", "--output", metavar='OUTPUT', required=False,
                    type=str, default=DEFAULT_OUT,
                    help="optional param.")
    # Log options
    ap.add_argument('-v', '--verbose', action="store_true",
                    help="Log option: Write debug messages.")

    arg = ap.parse_args()
    return arg


def main():
    arg = parse_args()
    init_logs(arg, log)

    seasons = arg.seasons
    output = arg.output

    # COLLECTING
    # **********************************
    log.info(u'Collecting for Seasons: {}'.format(seasons))
    historical_data = get_seasons(seasons)

    # DUMPING
    # **********************************
    log.info(u'Dumping to {}'.format(output))
    historical_data.to_csv(output, index=False)
    return

if __name__ == "__main__":
    main()

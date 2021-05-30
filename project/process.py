
# -*- coding: utf-8 -*-
"""
title: process.py
project: Link-Budget-Toolbox
date: 09/05/2021
author: Jesper Frijns
"""

# Two ways of importing the link element classes
import project.link_element as le
from pathlib import Path
import yaml
import pandas as pd
from project.unit_conversion import convert_SI_units
from project.settings import CONFIGS_DIR, DEFAULT_APP_CONFIG



def load_from_yaml(file):
    with open(file, 'r') as f:
        data = yaml.full_load(f)
    return data

def save_to_yaml(d:dict, filename:str):
    '''Save dictionary to yaml, with a specified filename

    Parameters
    ----------
    d : dict
        Dictionary to save to YAML
    filename : str
        Filename of YAML. If only a filename is passed, the save location
        defaults to "./configs/". This can be overwritten if a filepath is given
    '''
    # Convert to Path object, makes manipulation easier in the future
    filepath = Path(filename)

    if filepath.suffix != '.yaml': # Wrong suffix given
        filepath = Path(filepath.parent, filepath.stem+'.yaml')

    if len(filepath.parts) == 1: # Only a filename is given, change save directory to default
        filepath = Path(CONFIGS_DIR, filepath.name)

    # Save data to YAML
    with open(filepath, 'w') as f:
        yaml.dump(d, f)

def read_user_data(user_data):
    '''Convert the link element inputs from the user_data dictionary to a dataframe

    Parameters
    ----------
    user_data: dict
        Dictionary containing the data and link elements the user has given

    Returns
    -------
    df_user_data : df
        Dictionary which gives along its rows per link element the link element name, link type, input type,
        gain loss and parameters, based on the user input in the dictionary user_data
    '''

    df_user_data = pd.DataFrame.from_dict(user_data['elements']).T.reset_index().rename(columns={'index' : 'name'})

    return df_user_data


def fill_results_data(df_user_data, user_data):
    '''Get the gain/loss of each link element and write it to the results_data dictionary

    Parameters
    ----------
    df_user_data : df
        Dictionary which gives along its rows per link element the link element name, link type, input type,
        gain loss and parameters, based on the user input in the dictionary user_data

    Returns
    -------
    results_data : dict
        User_data dictionary which has been updated with the calculated gains/losses
    '''

    results_data = user_data

    for i in range(len(df_user_data)):
        # calculation step

        link_type = df_user_data.get("link_type")[i]
        link_class = f'{link_type}_LinkElement'


        if link_type == 'GENERIC':     # Generic (parent) link element class, takes 3 arguments
            link_class = f'LinkElement'
            result_gain_loss = (eval('le.' + link_class +
                                     '(df_user_data.get("name")[i], \
                                     df_user_data.get("input_type")[i],\
                                     df_user_data.get("gain_loss")[i])')).gain

        elif df_user_data.get("parameters")[i] == None: # Specific Link element, no parameters
            result_gain_loss = (eval('le.' + link_class +
                                     '(df_user_data.get("name")[i], \
                                     df_user_data.get("input_type")[i],\
                                     df_user_data.get("gain_loss")[i], \
                                     dict())')).gain

        else:           # All other link elements with parameters given
            result_gain_loss = (eval('le.' + link_class +
                                     '(df_user_data.get("name")[i], \
                                     df_user_data.get("input_type")[i],\
                                     df_user_data.get("gain_loss")[i], \
                                     df_user_data.get("parameters")[i])')).gain

        #update step
        results_data['elements'][df_user_data.get("name")[i]]["gain_loss"] = result_gain_loss

    return results_data




def main_process(user_data):
    '''Use user_data dictionary to calculate gains/losses to create a results_data dictionary

    Parameters
    ----------
    user_data: dict
        Dictionary containing the data and link elements the user has given

    Returns
    -------
    results_data : dict
        User_data dictionary which has been updated with the calculated gains/losses
    '''
    # Convert parameter units to standard SI base units
    convert_SI_units(user_data)

    results_data = fill_results_data(read_user_data(user_data), user_data)

    return results_data



if __name__ == '__main__':

    default_file = DEFAULT_APP_CONFIG

    data = load_from_yaml(default_file)

    main_process(data)






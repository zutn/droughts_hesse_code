import pandas as pd
import numpy as np
import sys
from matplotlib import pyplot as plt
import os


def print_balance(df):
    """Prints the mean annual water balance"""
    values = {v: df[v].mean() * 365 for v in 'PEQ'}

    return 'P={P}, E={E} Q={Q} mm/a'.format(**values)


def ETcorrection(df: pd.DataFrame):
    """
    Calculates a ET correction factor to close the water balance of the catchments

    [citation needed]

    :param df: A dataframe of Catchment timeseries data
    :return: Correction factor for all catchments
    """
    print(df)
    totE = df.E.sum()  # total ET in mm over whole period

    balance = (df.P - df.E - df.Q).sum()  # water balance over whole period

    rel_diff = balance / totE  # water balance error relative to ET

    return rel_diff + 1  # Factor for ET


def corrected_ET(df: pd.DataFrame):
    """
    Corrects a single E
    """
    fET = ETcorrection(df)
    return df.E * fET


def ETcorrection_all(dataframes: dict):
    """
    Calculates all ETcorrection factors for all catchments
    :param dataframes: A dict of all catchment dataframes
    :return: pd.Series
    """
    return pd.Series({k: ETcorrection(v) for k, v in dataframes.items()})


def correct_and_save_ET(dataframes:dict):
    """
    Corrects the ET for all catchments and saves it in the original datafraes
    """
    for catch in dataframes.keys():
        df = dataframes[catch]
        df["E_cor"] = corrected_ET(df)


def plot_correction_effect(dataframes: dict):
    """Makes violin plots to compare corrected and uncorrected ET"""
    plt.violinplot([[dataframes[df].E.mean() * 365 for df in dataframes],
                [dataframes[df].E_cor.mean() * 365 for df in dataframes]])


def plot_storage(dataframes: dict, attribs: pd.DataFrame):
    """
    Plots the storage development over the whole period
    :param dataframes:
    :param attributes:
    :return:
    """
    for catch in dataframes.keys():
        df = dataframes[catch]
        fET = ETcorrection(df)
        print(catch, attribs.loc[catch].gauge, fET)
        plt.plot(np.cumsum(df.P - df.E * fET - df.Q), label=attribs.loc[catch].gauge,
                 color="grey", linewidth=0.5)
        plt.ylabel('S(t) [mm]')


if __name__ == '__main__':
    # Get add the whole package to the path
    file_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.sep.join(file_dir.split(os.sep)[:-2]))
    import preprocessing.cleaned_data.create_cleaned_data_table as ccdt
    dataframes = ccdt.get_table_dict()
    attribs = ccdt.get_attributes()
    correct_and_save_ET(dataframes)
    
  #  plot_storage(dataframes, attribs)
    plot_correction_effect(dataframes)
    plt.show()
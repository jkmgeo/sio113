"""A collection of utilities for petrology and geochemistry

License:    CC BY-SA 
Author:     James K. Muller
Github:     jkmgeo
Email:      jamuller@ucsd.edu
"""

# import dependencies
import os
import pandas as pd

# built-in data directory:
include_dir = "include"

# built-in data files:
bse_file = "bse.csv"

################ ################
# specify default attributes/params
################ ################

# ELEMENTS FOR NORMALIZATION:

extended = [
    "Cs", "Rb", "Ba", "Th", 
    "Nb", "U", "La", "Ce", 
    "Pb", "Nd", "Sr", "Sm", 
    "Zr", "Hf", "Eu", "Gd", 
    "Tb", "Dy", "Er", "Y", 
    "Yb", "Lu", "Sc", "Cr", 
    "Ni"
] # modified after Hofmann (1997, Nature)

ree = [
    "La", "Ce", "Pr", "Pm", 
    "Nd", "Sm", "Eu", "Gd", 
    "Tb", "Dy", "Ho", "Er", 
    "Tm", "Yb", "Lu"
] # lanthanides, sorted by increasing Z number

# BUILT-IN DATA:

bse = pd.read_csv(
    os.path.join(os.getcwd(), include_dir, bse_file),
    index_col = "Element"
); # primitive mantle (McDonough & Sun, 1995, Chem. Geol.)

################ ################
# util: CamelCase
################ ################

def camel(el):
    """Force elemental abbreviation to camel case

    Parameters
    ----------
    el: str
        elemental abbreviation. Will not function as expected for compound 
        formulae, e.g., oxide species.

    Returns
    -------
    el_camel: str
        elemental abbreviation in camel case

    """
    el_camel = el[0].upper() + el[1:].lower()
    return el_camel

################ ################
# util: normalize to PM
################ ################

def pm_norm(
    df, 
    cols = "ree", 
    squeeze = True, 
    interp = False, 
    norm_vals = "bse"
):
    """
    
    _NORM_alize geochemical elements to _P_rimitive _M_antle of McDonough & 
    Sun (1995, Chem. Geol.).
    
    Parameters
    ----------
    df: pandas DataFrame
        Tidy geochemistry dataset, where each column is a variable, and each 
        row is an observation (i.e., measurement or sample). Geochemical 
        concentrations are expected as elemental (i.e., not oxide) abundances 
        in ppm units, and columns must be periodic table abbreviations (e.g., 
        "La" for lanthanum, though function will be string format agnostic).
        
    cols: str, list
        Elements from `df` to be normalized. Elements *MUST* be in `df`
        
        - If `str`: One of {`ree`, `extended`, or elemental abbreviation}, 
            where:
            `ree = [
                "La", "Ce", "Pr", "Pm", "Nd", 
                "Sm", "Eu", "Gd", "Tb", "Dy", 
                "Ho", "Er", "Tm", "Yb", "Lu"
            ] # sorted by increasing Z number`
            
            and 
            
            `extended = [
                "Cs", "Rb", "Ba", "Th", "Nb", 
                "U", "La", "Ce", "Pb", "Nd", 
                "Sr", "Sm", "Zr", "Hf", "Eu", 
                "Gd", "Tb", "Dy", "Er", "Y", 
                "Yb", "Lu", "Sc", "Cr", "Ni"
            ] # modified after Hofmann (1997, Nature)`
            
        - If `list`: List of elemental abbreviations.
        
    squeeze: bool
        Specify whether to compress norm_df to include only those columns in 
        both input and normalizing datasets (i.e., intersection)
    
    interp: bool
        Specify whether to fill empty columns using linear interpolation of 
        neighboring columns. Requires `squeeze = False`.
    
    norm_vals: pandas DataFrame
        Tidy dataframe of normalizing values, where indices are chemical 
        element abbreviations, and first column has abundance data. Defaults 
        to Bulk Silicate Earth (BSE), a.k.a. pyrolite/Primitive Mantle (PM) of 
        McDonough & Sun (1995, Chem. Geol., doi:10.1016/0009-2541(94)00140-4).
    
    Returns
    -------
    norm_df: str or pandas DataFrame
        Tidy dataset of normalized data. Shape will be equal to shape of input 
        `df` if `squeeze = False`, else will be more narrow. Dataframe may be of different shape 
        than input `df` because columns of output `norm_df` are intersection 
        of variables in `df` and indices (i.e., elemental abbreviations) of 
        normalizing data, from `./include/bse.csv`.
        
    To Do
    -----
    [ ]:    add check for `subset_cols` in `df` (presently assumed)
    [ ]:    add `squeeze = False` functionality (i.e., add in columns of NaN)
    [ ]:    add `interp = True` functionality (i.e., fill columns)
    [ ]:    increase `spider_plot` functionality, such as legends, colorbars
        
    """
    import numpy as np
    
    # get elemental abbreviations as list if not passed as input
    if type(cols) is str:
        
        if cols.lower() == "ree":
            cols = ree
            pass
        
        elif cols.lower() == "extended":
            cols = extended
            pass
        
        else:
            cols = [cols] if cols in norm_vals.index else False
        pass
    
    # get normalizing values as dataframe
    if type(norm_vals) is str:
        if norm_vals.lower() == "bse":
            norm_vals = bse
            pass
        pass
    
    # find intersecting cols in `cols` and `norm_vals`
    if cols:
        subset_cols = [i if camel(i) in norm_vals.index else None \
                       for i in cols]
    
        # possible solution to check if `cols` in `df`:
        subset_cols = [i if camel(i) in norm_vals.index and \
                       i in df.columns else None for i in cols]
    
        # confirm >= 1 element found
        if any(subset_cols) is False:

            # set flag to `False` if all items are `None`
            subset_cols = False

            pass

        else:

            try:

                # find if any items are `None`
                n = subset_cols.count(None)
                
                # remove all `None` items
                for count in range(n):
                    subset_cols.pop(subset_cols.index(None))
                    pass
                pass
            
            except:
                # handle if no items are `None`
                pass
            
            pass
        pass
    
    else:
        subset_cols = False
        pass
    
    # normalization of any suitable columns
    if subset_cols:
        
        # get subset of input dataframe
        df_to_norm = df[subset_cols]
        
        # get normalizing values for relevant elements
        normers = np.array([norm_vals.loc[camel(i)].values[0] for i in subset_cols])
        
        # normalize
        norm_df = df_to_norm / normers
        
        # format columns
        norm_df.columns = [camel(i) for i in norm_df.columns]
        
        pass
    
    try:
        return norm_df
    except:
        pass
    pass

################ ################
# util: plot spidergram
################ ################

def spider_plot(
    df, 
    alpha = 0.5
):
    """
    _PLOT_ multi-element variation (_SPIDER_) diagram
    
    Parameters
    ----------
    df: pandas DataFrame
        data to plot; must be tidy
    alpha: float
        transparency of plot glyphs
    
    Returns
    -------
    fig: matplotlib.pyplot.Figure
        instance of figure
    ax: matplotlib.pyplot.Axes
        instance (or tuple) of Axes
    
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    
    # set default plot styling
    plt.style.use("bmh");
    
    # make plot objects
    fig, ax = plt.subplots();
    
    # plot data
    ax.plot(df.T, alpha = alpha, marker = "d");
    
    # update axes labels, limits, and scale:
    ax.set_ylabel("concentration / BSE");
    ax.set_yscale("log");
    
    return fig, ax

################ ################
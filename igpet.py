"""A collection of utilities for petrology and geochemistry"""

################ ################
# specify default parameters
################ ################

# elements for normalization
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
] # sorted by increasing Z number

################ ################
# util: CamelCase
################ ################

def camel(el):
    """Force elemental abbreviation to camel case

    Parameters
    ----------
    el: str
        elemental abbreviation

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

def pm_norm(df, cols = ree):
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
        Elements from `df` to be normalized.
        If `str`: One of {`ree`, `extended`, or elemental abbreviation}, 
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
            
        If `list`: List of elemental abbreviations.
    
    Returns
    -------
    norm_df: pandas DataFrame
        Tidy dataset of normalized data. Dataframe may be of different shape 
        than input `df` because columns of output `norm_df` are intersection 
        of variables in `df` and indices (i.e., elemental abbreviations) of 
        normalizing data, from `./include/bse.csv`.
    
    """
    import pandas as pd
    import numpy as np
    
    # load normalizing dataset (i.e., primitive mantle composition)
    bse = pd.read_csv("./include/bse.csv", index_col = "Element")
    
    # get elemental abbreviations if not passed into function
    if cols.lower() == "ree":
        cols = ree
        pass
    elif cols.lower() == "extended":
        cols = extended
        pass
    
    # find columns common to `df` and `bse`
    if type(cols) is list:
        subset_cols = [i if camel(i) in bse.index else None for i in cols]
        
        # confirm >= 1 element found
        if any(subset_cols) is False:
            # set flag to `False` if all items are `None`
            subset_cols = False
            pass
        
        else:
            try:
                # find if any items are `None`
                n = subset_cols.count(None)
                
                for count in range(n):
                    subset_cols.pop(subset_cols.index(None))
                    pass
                pass
            
            except:
                # handle if no items are `None`
                pass
            pass
        pass
    
    elif type(cols) == str:
        subset_cols = [cols] if cols in bse.index else False
        pass
    
    # normalization of any suitable columns
    if subset_cols:
        
        # get subset of input dataframe
        df_to_norm = df[subset_cols]
        
        # get normalizing values for relevant elements
        bse_vals = np.array([bse.loc[camel(i)].values[0] for i in subset_cols])
        
        # normalize
        norm_df = df_to_norm / bse_vals
        
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

def spider_plot(df, alpha = 0.5):
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
    
    # make plot
    fig, ax = plt.subplots();
    
    ax.plot(df.T, alpha = alpha);
    
    # update axes labels, limits, and scale:
    ax.set_ylabel("concentration / BSE");
    ax.set_yscale("log");
    
    return fig, ax

################ ################
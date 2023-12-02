""" Pandas Utility Functions

"""
from typing import Any, Optional, Union

import pandas as pd


def split_df_rows(df, bool_series):
    """ Split dataframe by rows into two dataframes based on boolean series

    Args:
        df (pd.DataFrame): dataframe to be split
        bool_series (pd.Series): series of booleans with index matching df

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: first dataframe has rows that are True in bool_series, second dataframe has
            rows that are False in bool_series
    """
    return df[bool_series], df[~bool_series]


def move_cols(df, move_dict):
    """ Move columns (given by name) to position (given by name or index)

    index values can be negative
    Consider that moves are made sequentially, so index values may not be as expected after a move.

    Args:
        df (pd.DataFrame):
        move_dict (dict): key from_column name (str), value to_column name (str) or index (int)

    Returns:
        pd.DataFrame: df with columns moved
    """
    num_cols = len(df.columns)

    for from_col, to_col in move_dict.items():
        if isinstance(to_col, str):
            to_col = df.columns.get_loc(to_col)
        elif to_col < 0:
            to_col = num_cols + to_col

        df.insert(to_col, from_col, df.pop(from_col))

    return df


def to_html(df, header=True, head_align="center", index=False, na_rep="", frac=2, comma=False, hl_rows=None,
            hl_cells=None, cell_align="left", rgd_fmt_list=(), dollar_fmt_list=()):
    """ Custom to_html function using the dataframe Styler

    Args:
        df (pd.DataFrame):
        header (boolean): show column headers or not. Default True
        head_align (str): alignment of column headers. Default "center"
        index (boolean): show index or not. Default False
        na_rep (str): Default ""
        frac (Union[int, dict]): number of fractional digits. If int, only applied to float and float64 columns.
            If dict, can include key/value **DEF**/int to set default fractional digits to int. If **DEF** not included,
            columns not in dict will have no rounding set. Default 2.
        comma (boolean): True to include comma formatting in int, int64, float, float64 columns. Default False

        Optional[list[[column, val, color] or [Int64Index, color]])
        hl_rows (Optional[list[Union[list[str, Any, str], list[pd.Int64Index, str]]]]): Default None.
            Can alternate sublist type.
            [column, val, color]: highlight rows with specified values in specified columns.
                [[column, val, color], ...] in decreasing priority. Unmatched rows are given default background.
            [Int64Index, color]: highlight rows with specified index. [[Int64Index, color], ...]. Unspecified rows are
                give default background
        hl_cells (Optional[list[list[str, list[int], list[str]]]]): highlight cells.
            each sublist has [color, indexes, col(s)]. Default None
        cell_align (Union[str, dict]): str to align all cells with same alignment. dict of alignment (key) to list of
            column header names to align all cells in column with same alignment. Default "left"
        rgd_fmt_list (list[str]): list of columns names of type int, int64, float, float64. format with
            prepended "$". negative values have red font color. positive values have green font color. Default ()
        dollar_fmt_list (list[str]): list of columns names of type int, int64, float, float64. format with
            prepended "$". Default ()

    Returns:
        str: html
    """
    # combine these into 1 list. these columns will have $ prepended
    dollar_fmt_list = tuple(rgd_fmt_list) + tuple(dollar_fmt_list)

    styler = df.style

    if not header:
        styler.hide_columns()
    if not index:
        styler.hide_index()

    # set head align and all borders
    border_prop = "1px solid grey"
    styler.set_table_styles([{"selector": "", "props": [("border", border_prop)]},
                             {"selector": "tbody td", "props": [("border", border_prop)]},
                             {'selector': 'th', 'props': [('text-align', head_align), ("border", border_prop)]}])
    styler.set_properties(border=border_prop)
    if isinstance(cell_align, dict):
        for align, cols in cell_align.items():
            styler.set_properties(subset=cols, **{"text-align": align})
    elif isinstance(cell_align, str):
        styler.set_properties(**{"text-align": cell_align})

    # set comma for all number fields
    comma_str = "," if comma else ""
    # set frac on all float or float64 columns if is an int, otherwise set by dict
    if isinstance(frac, int):
        frac_dict = {}
    else:  # isinstance dict
        frac_dict = {col: ("$" if col in dollar_fmt_list else "") + "{0:" + comma_str + "." + str(f) + "f}"
                     for col, f in frac.items()}
        if "**DEF**" in frac:
            frac = frac["**DEF**"]
            frac_dict.pop("**DEF**")
        else:
            frac = None

    for col in df.columns:
        if col not in frac_dict:
            dol_str = ("$" if col in dollar_fmt_list else "")
            if df[col].dtype in ("float", "float64"):
                if frac is not None:
                    frac_dict[col] = dol_str + "{0:" + comma_str + "." + str(frac) + "f}"
            elif df[col].dtype in ("int", "int64"):
                frac_dict[col] = dol_str + "{0:" + comma_str + ".0f}"

    styler.format(frac_dict, na_rep=na_rep).set_na_rep(na_rep)

    if hl_rows is not None:
        def hl(row):
            row_bg = None
            # args = [column, value, color]
            for hl_row in hl_rows:
                if isinstance(hl_row[0], str):
                    if row[hl_row[0]] == hl_row[1]:
                        row_bg = ['background-color: ' + hl_row[2]]
                        break
                else:  # isinstance(hl_row[0], pd.Int64Index)
                    if row.name in hl_row[0]:
                        row_bg = ['background-color: ' + hl_row[1]]
            return ([""] if row_bg is None else row_bg) * len(row)
        styler.apply(hl, axis=1)

    if hl_cells is not None:
        for lst in hl_cells:  # lst has [color, indexes, col(s)]
            if len(lst[1]) > 0:
                styler.applymap(lambda x: "background-color: " + lst[0], subset=pd.IndexSlice[lst[1], lst[2]])

    if len(rgd_fmt_list) > 0:
        styler.apply(lambda s: ["color: " + ("red" if x < 0 else "green") for x in s], subset=rgd_fmt_list)

    return styler.render()


def ins_row_at_end(df, row):
    """ Convenience function for df.append(). Insert row at end of dataframe with numeric index.

    This isn't as trivial as it may seem. iloc can't increase the length of the df, so .iloc[len(df)] wont work.
    .loc[len(df)] may overwrite an existing row if len(df) is an existing index value.
    This function creates a new index value by adding 1 to the max existing index value or uses 0 if no index values.

    Args:
        df (pd.DataFrame): dataframe with a numeric index
        row (list): length of row should equal number of columns in df for expected behavior

    Returns:
        pd.DataFrame: df with row inserted at end with unique index value and no other rows changed
    """
    df.loc[0 if len(df) == 0 else (df.index.max() + 1)] = row
    return df


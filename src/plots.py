import datetime
import pandas as pd
import sys
import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from typing import List

# CI
efgreen         = "#005953"
eflightgreen    = "#69a3a2"
eflightergreen  = "#a2c5c4"
eflightestgreen = "#e6efee"


def parse_status_dict(status_dict: dict) -> tuple[int, int, int, int]:
    ''' Parse a single registration status dictionary.
    Missing values will be set to zero. '''

    new       = status_dict.get("new", 0)
    approved  = status_dict.get("approved", 0)
    partially = status_dict.get("partially paid", 0)
    paid      = status_dict.get("paid", 0)
    checkedin = status_dict.get("checked in", 0)
    return (new, approved, partially, paid, checkedin)


def parse_sponsor_dict(sponsor_dict: dict) -> tuple[int, int, int]:
    ''' Parse a single sponsor status dictionary.
    Missing values will be set to zero. '''

    normal       = sponsor_dict.get("normal", 0)
    sponsor      = sponsor_dict.get("sponsor", 0)
    supersponsor = sponsor_dict.get("supersponsor", 0)
    return (normal, sponsor, supersponsor)


def split_tuplecol(df: pd.core.frame.DataFrame,
                   incol: str,
                   outcols: List[str]) -> pd.core.frame.DataFrame:
    ''' Given a column of tuples, make a set of new columns,
        containing the tuple elements. Drop input column. '''

    # Sanity check: Make sure every element of the input column contains
    # an iterable with as many elements as we have output columns.
    if not all(df[incol].apply(len) == len(outcols)):
        sys.exit(f"split.tuplecol: Malformed entry in column {incol}.")
    
    for i, outcol in enumerate(outcols):
        df[outcol] = [x[i] for x in df[incol]]

    df.drop(columns = [incol], inplace = True)
    return df


def read_parse_input(filename: str = "./data/log.txt") -> pd.core.frame.DataFrame:
    # For now, we only need the time stamp, the total count (for sanity
    # checks), the reg status and the sponsor category column.
    try:
        df = pd.read_json(filename, lines = True)
    except ValueError as e:
        sys.exit(f"read_parse_input: Error while loading source data: {e}")
    df = df.loc[:, ["CurrentDateTimeUtc", "TotalCount", "Status", "Sponsor"]]
    
    # Parse timestamp column via direct conversion
    df.CurrentDateTimeUtc = pd.to_datetime(df.CurrentDateTimeUtc)
    
    # Parse 'Status' and 'Sponsor' column from dicts to tuples.
    df.Status  = df.Status.apply(parse_status_dict)
    df.Sponsor = df.Sponsor.apply(parse_sponsor_dict)
    
    # Turn the two tuple columns into sets of individual columns.
    status_cols  = ["new", "approved", "partial", "paid", "checkedin"]
    sponsor_cols = ["normal", "sponsor", "supersponsor"]
    df           = split_tuplecol(df      = df,
                                  incol   = "Status",
                                  outcols = status_cols)
    df           = split_tuplecol(df      = df,
                                  incol   = "Sponsor",
                                  outcols = sponsor_cols)
    
    return df



def daywise(df: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    ''' Calculate day-wise count'''

    # Working copy
    out          = df.copy()

    # Get last count for every day
    out["Date"]  = pd.to_datetime(df['CurrentDateTimeUtc']).dt.strftime('%m/%d/%Y')
    out          = out.groupby("Date").agg("last").reset_index()
    out          = out.loc[:, ["Date", "TotalCount"]]
    
    # Add day index, shifted by offset of three,
    # s.t. day 0 is the day of reg opening
    out["idx"] = np.arange(0, len(out)) - 3

    return out


def tripleplot(df: pd.core.frame.DataFrame,
               df_last: pd.core.frame.DataFrame) -> None:
        
    # Prepare figure
    s = 20
    fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize = (15,15))
    plt.subplots_adjust(hspace = .3, wspace=.3)
    axes.flat[0].set_visible(False)
    axes.flat[1].set_visible(False)
    axes.flat[2].set_visible(False)
    axes.flat[3].set_visible(False)


    ###############
    # Annotations #
    ###############
     
    annot    = \
f'''Nothing to see here yet.
For questions, contact @GermanCoyote.'''
    axes.flat[3].annotate(text     = annot,
                          xy       = (0.005, 0.005),
                          xycoords = 'figure fraction',
                          fontsize = s/3)

    # Export
    plt.savefig(fname       = "./out/Fig1.svg",
                bbox_inches = "tight")


if __name__ == "__main__":
    # This year's data, from our own logger
    # ef2024 = read_parse_input()
    
    # Last year's data
    # ef2023 = read_parse_input("./data/log2024.txt")
    
    tripleplot(None, None)

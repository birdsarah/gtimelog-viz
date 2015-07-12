import pandas as pd
import numpy as np


def get_raw_df():
    raw = pd.read_table('timelog.txt', quotechar=' ', sep=': ', names=['timestamp', 'activity'], engine='python',)

    # Set the column types

    raw.timestamp = pd.to_datetime(raw.timestamp)
    raw = raw.drop_duplicates()

    ### Build the times
    raw['end'] = raw.timestamp
    raw['start'] = raw['end'].shift(1)

    raw['start'] = np.where(
        raw['activity'] == 'start',  # If the activity is start
        raw['timestamp'],  # Set the start to timestamp
        raw['start'],  # Else leave it as start
    )

    raw['delta'] = raw.end - raw.start

    return raw


def keep_top_level_cats_only(gt_df):
    """
    Takes a gtimelog DataFrame, and removes the non-work categories, and
    boils the other categories down to their high-level category.
    """
    gt_df = gt_df[~gt_df.activity.str.contains(r'\*\*\*')]
    # Boil down the categories to the main work categories
    gt_df.activity = gt_df.activity.str.split(r' ').str[0]

    return gt_df

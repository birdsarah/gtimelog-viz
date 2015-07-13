import pandas as pd
import numpy as np

from utils import timelog_path


def _get_raw_df():
    raw = pd.read_table(timelog_path, quotechar=' ', sep=': ', names=['timestamp', 'activity'], engine='python',)

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


def get_work_df():
    """
    Takes a gtimelog DataFrame, and removes the non-work categories
    """
    gt_df = _get_raw_df()
    gt_df = gt_df[~gt_df.activity.str.contains(r'\*\*\*')]
    return gt_df


def add_parent_activity(gt_df):
    """
    Takes a gtimelog DataFrame, and removes the non-work categories, and
    boils the other categories down to their high-level category.
    """
    # Boil down the categories to the main work categories
    gt_df['parent activity'] = gt_df.activity.str.split(r' ').str[0]
    return gt_df

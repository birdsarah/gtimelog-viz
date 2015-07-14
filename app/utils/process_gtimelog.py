import pandas as pd
import numpy as np

from . import timelog_path


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


def add_processed_columns(gt_df, general_activity_name='general'):
    """
    Takes a gtimelog DataFrame, and adds the following columns:
        * 'human' - the time delta in hours to 2 decimal places
        * 'parent_activity' - if the activity is 'Test data - sub category', parent is 'Test data'
        * 'sub_activity' - if the activity is 'Test data - sub category', sub is 'sub category'
    Also:
        * If the activity is the same as the parent activity,
          then sub_activity is set to general_activity_name
        * capitalizes the new activity columns
    """
    gt_df['human'] = gt_df.delta.dt.seconds / (60 * 60)
    gt_df.human = gt_df.human.round(2)

    gt_df['parent_activity'] = gt_df.activity.str.split(' - ').str[0]
    gt_df.parent_activity = gt_df.parent_activity.str.capitalize()

    gt_df['sub_activity'] = gt_df.activity.str.split(' - ').str[1]
    gt_df.sub_activity = np.where(
        gt_df.activity == gt_df.parent_activity,
        general_activity_name,
        gt_df.sub_activity
    )
    gt_df.sub_activity = gt_df.sub_activity.str.capitalize()
    return gt_df

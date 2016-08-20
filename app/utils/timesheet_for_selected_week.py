import pandas as pd

from .chart_utils import make_mdl_table


def make_timesheet(one_week, group_by, start, end):
    """
    one_week is the dataframe that contains one week of data
    group_by is the column to groupby (other than date)
    start and end are start and end of the week.
    """
    df = one_week.groupby([one_week.timestamp.dt.date, group_by]).sum().unstack(1)
    df.columns = df.columns.levels[1][df.columns.labels[1]]
    df.columns.name = None
    df.index = pd.DatetimeIndex(df.index)
    all_date_index = pd.DatetimeIndex(start=start.date(), end=end.date(), freq='d')
    df = df.join(pd.DataFrame(index=all_date_index), how='outer').fillna(0)
    df.index = df.index.format(formatter=lambda x: x.strftime("%a %b %d"))
    df = df.T
    df['Total'] = df.sum(axis=1)
    return df


def get_timesheet(raw, start, end):
    raw = raw[raw.activity != 'start']
    week = raw[(raw.timestamp.dt.date >= start.date()) & (raw.timestamp.dt.date <= end.date())]

    if week.empty:
        return '<p class="nothing">Nothing to report!</p>'

    parent = make_timesheet(week, week.parent_activity, start, end)

    individual = make_timesheet(week, week.formatted_activity, start, end)
    individual = individual.reset_index()

    def get_proportion_of_parent(r):
        activity_total = r['Total']
        activity = r['index']
        parent_total = parent['Total'][activity.split(' ')[0]]
        return '%i%%' % ((activity_total / parent_total) * 100)

    individual['%'] = individual.apply(get_proportion_of_parent, axis=1)
    individual = individual.set_index('index')
    individual.index.name = None

    joined = pd.concat([parent, individual])[list(individual.columns)].fillna('')

    return make_mdl_table(joined)

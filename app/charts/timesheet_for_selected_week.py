

def get_timesheet(df, start, end):
    df = df[df.activity != 'start']
    week = df[(df.timestamp.dt.date >= start.date()) & (df.timestamp.dt.date <= end.date())]
    grouped = week.groupby([week.timestamp.dt.date, week.formatted_activity]).sum().unstack(0).fillna(0)
    levels = grouped.columns.levels
    labels = grouped.columns.labels
    grouped.columns = levels[1][labels[1]]
    grouped.index.names = ['']
    return grouped.to_html(classes=["mdl-data-table", "mdl-js-data-table"], index_names=False)

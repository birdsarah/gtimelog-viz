import datetime

from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, Range1d, FactorRange,
    HoverTool, PanTool, WheelZoomTool
)


def get_plot(processed, today):

    two_days_ago = today - datetime.timedelta(days=2)
    one_week_ago = today - datetime.timedelta(weeks=1)
    #two_week_ago = today - datetime.timedelta(weeks=2)
    #three_week_ago = today - datetime.timedelta(weeks=3)

    start = two_days_ago
    end = today

    one_week = processed[(processed.timestamp >= start) & (processed.timestamp <= end)]
    one_week = one_week[one_week.activity != 'start']
    one_week['activity_bottom'] = one_week.formatted_activity + ':0.1'
    one_week['activity_top'] = one_week.formatted_activity + ':0.9'

    source = ColumnDataSource(one_week[['start', 'end', 'activity_top', 'activity_bottom', 'human']])
    activities = list(one_week.formatted_activity.unique())
    activities = sorted(activities)
    n = len(activities)
    height = 75 * n

    p = figure(
        x_range=Range1d(start=start, end=end),
        y_range=FactorRange(factors=activities),
        tools='reset', width=600, height=height
    )
    p.quad(left='start', right='end', top='activity_top', bottom='activity_bottom', source=source)
    p.add_tools(HoverTool(tooltips='@human hrs'))
    p.add_tools(PanTool(dimensions=['width']))
    p.add_tools(WheelZoomTool(dimensions=['width']))
    return p

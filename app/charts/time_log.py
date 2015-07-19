import datetime

from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource,
    Range1d,
    FactorRange,
    HoverTool,
)
from .constants import COLOR_PRIMARY, COLOR_PRIMARY_CONTRAST, COLOR_PRIMARY_DARK


def get_plot(processed, today):
    start = today - datetime.timedelta(days=2)  # Start the plot two days ago
    end = today

    one_week = processed[(processed.timestamp >= start) & (processed.timestamp <= end)]
    one_week = one_week[one_week.activity != 'start']
    one_week['activity_bottom'] = one_week.formatted_activity + ':0.1'
    one_week['activity_top'] = one_week.formatted_activity + ':0.9'

    source = ColumnDataSource(one_week[['start', 'end', 'activity_top', 'activity_bottom', 'human']])
    activities = list(one_week.formatted_activity.unique())
    activities = sorted(activities)
    n = len(activities)
    height = 50 * n

    p = figure(
        x_range=Range1d(start=start, end=end),
        y_range=FactorRange(factors=activities),
        tools='reset', toolbar_location=None,
        width=400, height=height,
        background_fill=COLOR_PRIMARY,
        border_fill=COLOR_PRIMARY,
        outline_line_color=None,
    )
    for axis in [p.xaxis[0], p.yaxis[0]]:
        axis.major_label_text_color = COLOR_PRIMARY_CONTRAST
        axis.axis_line_color = COLOR_PRIMARY
        axis.major_tick_line_color = COLOR_PRIMARY

    for grid in [p.xgrid[0], p.ygrid[0]]:
        grid.grid_line_color = COLOR_PRIMARY_DARK

    p.quad(left='start', right='end', top='activity_top', bottom='activity_bottom', source=source)
    p.add_tools(HoverTool(tooltips='@human hrs'))
    return p

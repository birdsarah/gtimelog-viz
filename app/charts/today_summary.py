import datetime
from bokeh.charts import Bar
from bokeh.models import Legend, LinearAxis, CategoricalAxis, GlyphRenderer, HoverTool
from bokeh.models import DatetimeTickFormatter

from .constants import COLOR_PRIMARY, COLOR_PRIMARY_CONTRAST
from .chart_utils import get_palette


def get_data(raw):
    today = datetime.date(2015, 7, 7)
    yesterday = today - datetime.timedelta(1)

    sliced = raw[(raw.timestamp.dt.date == today) | (raw.timestamp.dt.date == yesterday)]
    sliced = sliced[sliced.activity != 'start']
    sliced['human'] = sliced.delta.dt.seconds / (60 * 60)
    sliced = sliced[['activity', 'timestamp', 'human']]

    summed = sliced.groupby(['activity', sliced.timestamp.dt.date]).sum()
    summed = summed.unstack('activity')
    levels = summed.columns.levels
    labels = summed.columns.labels
    summed.columns = levels[1][labels[1]]
    summed.sort_index(inplace=True)
    summed.fillna(0, inplace=True)
    return summed


def get_plot(raw):
    data_frame = get_data(raw)
    palette = get_palette(list(data_frame.columns))
    plot = Bar(
        data_frame, tools='', legend=True,
        palette=palette,
        width=600, height=600,
    )
    return plot

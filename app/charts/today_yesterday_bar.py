import datetime
from bokeh.charts import Bar

from .chart_utils import get_palette


def get_data(raw):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(1)

    sliced = raw[(raw.timestamp.dt.date == today) | (raw.timestamp.dt.date == yesterday)]
    sliced = sliced[sliced.activity != 'start']

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

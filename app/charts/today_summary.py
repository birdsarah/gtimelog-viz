import pandas as pd

from bokeh.charts import Bar
from bokeh.models import Range1d, DataTable, ColumnDataSource, TableColumn

from .chart_utils import get_palette


def make_bar(color, category, data):
    bar_plot = Bar(data, width=200, height=200, palette=[color, '#dddddd'], tools='', stacked=True)
    bar_plot.toolbar_location = None
    bar_plot.outline_line_color = None
    bar_plot.y_range = Range1d(0, 8)
    bar_plot.min_border = 5
    bar_plot.min_border_top = 10
    return bar_plot


def make_table(category, data):
    totalled = pd.concat(
        [
            data,
            pd.DataFrame({'human': data.human.sum()}, index=['%s - Total' % category])
        ]
    )
    source = ColumnDataSource(totalled)
    table = DataTable(
        source=source,
        columns=[
            TableColumn(field="sub_activity", title=category),
            TableColumn(field="human", title="Total")
        ],
        width=200,
        height=150,
    )
    return table


def get_plot(data):
    categories = list(data.parent_activity.unique())
    palette = get_palette(categories)

    plots = {}

    for i, category in enumerate(categories):
        parent_df = data[data.parent_activity == category]
        summed = parent_df.groupby('sub_activity').sum().sort('human', ascending=False)
        summed['from total'] = summed.human.sum() - summed.human
        bar_plot = make_bar(palette[i], category, summed)
        table = make_table(category, summed)
        plots[category + '_bar'] = bar_plot
        plots[category + '_table'] = table

    return categories, plots

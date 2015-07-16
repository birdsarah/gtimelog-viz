import pandas as pd

from bokeh.charts import Bar
from bokeh.models import (
    DataTable,
    ColumnDataSource,
    TableColumn,
    Legend,
    HoverTool,
    GlyphRenderer,
    CategoricalAxis,
    LinearAxis,
)

from .chart_utils import get_palette
from .constants import COLOR_PRIMARY, COLOR_PRIMARY_CONTRAST


def make_bar(color, data):
    plot = Bar(data, width=200, height=200, palette=[color, '#dddddd'], tools='', stacked=True)
    plot.toolbar_location = None
    plot.outline_line_color = None
    plot.min_border = 5
    plot.min_border_top = 10

    # Get chart items
    legend = plot.select({'type': Legend})
    hover = plot.select({'type': HoverTool})
    glyphs = plot.select({'type': GlyphRenderer})
    xaxis = plot.select({'type': CategoricalAxis})
    yaxis = plot.select({'type': LinearAxis})

    # Format chart properties
    plot.toolbar_location = None
    plot.background_fill = COLOR_PRIMARY
    plot.border_fill = COLOR_PRIMARY
    plot.outline_line_color = None
    plot.min_border_top = 0

    # Format legent
    legend.label_text_color = COLOR_PRIMARY_CONTRAST
    legend.border_line_color = COLOR_PRIMARY_CONTRAST

    # Tweak hover
    hover.tooltips = [('hours', '$y')]
    hover.point_policy = 'follow_mouse'

    # Format plots
    for g in glyphs:
        g.glyph.fill_alpha = 1
        g.glyph.line_color = None

    # Set xaxis properties
    xaxis.major_label_text_color = COLOR_PRIMARY_CONTRAST
    xaxis.major_label_orientation = 0
    xaxis.major_label_standoff = 15
    xaxis.major_tick_out = None
    xaxis.major_tick_in = None
    xaxis.axis_line_color = None

    # Set yaxis properties
    yaxis.major_label_text_color = COLOR_PRIMARY_CONTRAST
    yaxis.major_tick_out = None
    yaxis.major_tick_in = None
    yaxis.axis_line_color = None

    return plot


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
        width=300,
        height=200,
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
        bar_plot = make_bar(palette[i], summed)
        table = make_table(category, summed)
        plots[category + '_bar'] = bar_plot
        plots[category + '_table'] = table

    return categories, plots

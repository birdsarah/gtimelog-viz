import pandas as pd

from bokeh._legacy_charts import Bar
from bokeh.models import (
    Range1d,
    DataTable,
    ColumnDataSource,
    TableColumn,
    Legend,
    HoverTool,
    GlyphRenderer,
    CategoricalAxis,
    LinearAxis,
    SingleIntervalTicker,
    Grid,
)

from .chart_utils import get_palette, make_mdl_table
from .constants import COLOR_PRIMARY, COLOR_PRIMARY_CONTRAST, COLOR_PRIMARY_DARK


def make_bar(color, data):
    plot = Bar(data, width=200, height=200, palette=[color, COLOR_PRIMARY_DARK], tools='', stacked=True)
    plot.toolbar_location = None
    plot.outline_line_color = None
    plot.min_border = 5
    plot.y_range = Range1d(0, 10)

    # Get chart items
    legend = plot.select({'type': Legend})
    hover = plot.select({'type': HoverTool})
    glyphs = plot.select({'type': GlyphRenderer})
    xaxis = plot.select({'type': CategoricalAxis})
    yaxis = plot.select({'type': LinearAxis})
    ygrid = plot.select({'type': Grid})

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
    yaxis.ticker = SingleIntervalTicker(interval=3)

    ygrid.grid_line_color = None

    return plot


def make_table_widget(category, data):
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


def make_table_pandas(category, data):
    totalled = pd.concat([
        data,
        pd.DataFrame({'human': data.human.sum()}, index=['%s - Total' % category])
    ])
    return make_mdl_table(totalled[['human']], header=False)


def get_plot(data):
    categories = list(data.parent_activity.unique())
    palette = get_palette(categories)

    plots = {}
    tables = {}

    for i, category in enumerate(categories):
        parent_df = data[data.parent_activity == category]
        summed = parent_df.groupby('sub_activity').sum().sort('human', ascending=False)
        summed['from total'] = summed.human.sum() - summed.human
        bar_plot = make_bar(palette[i], summed)
        table = make_table_pandas(category, summed)
        plots[category + '_bar'] = bar_plot
        tables[category + '_table'] = table

    return categories, plots, tables

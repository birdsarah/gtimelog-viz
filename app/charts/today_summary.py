import datetime
from bokeh.charts import Bar
from bokeh.models import Legend, LinearAxis, CategoricalAxis, GlyphRenderer, HoverTool
from bokeh.models import DatetimeTickFormatter

from .utils import get_palette
import constants as c


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
        data_frame, tools='hover', legend=True,
        palette=palette,
        width=600, height=600,
    )
    # Get chart items
    legend = plot.select({'type': Legend})
    hover = plot.select({'type': HoverTool})
    glyphs = plot.select({'type': GlyphRenderer})
    xaxis = plot.select({'type': CategoricalAxis})
    yaxis = plot.select({'type': LinearAxis})

    # Format chart properties
    plot.toolbar_location = None
    plot.background_fill = c.COLOR_PRIMARY
    plot.border_fill = c.COLOR_PRIMARY
    plot.outline_line_color = None
    plot.min_border_top = 0

    # Format legent
    legend.label_text_color = c.COLOR_PRIMARY_CONTRAST
    legend.border_line_color = c.COLOR_PRIMARY_CONTRAST

    # Tweak hover
    hover.tooltips = [('hours', '$y')]
    hover.point_policy = 'follow_mouse'

    # Format plots
    for g in glyphs:
        g.glyph.fill_alpha = 1
        g.glyph.line_color = None

    # Set xaxis properties
    xaxis.major_label_text_color = c.COLOR_PRIMARY_CONTRAST
    xaxis.major_label_orientation = 0
    xaxis.major_label_standoff = 15
    xaxis.formatter = DatetimeTickFormatter(
        formats={
            'years': ["%a %d %b"],
        }
    )
    xaxis.major_tick_out = None
    xaxis.major_tick_in = None
    xaxis.axis_line_color = None

    # Set yaxis properties
    yaxis.major_label_text_color = c.COLOR_PRIMARY_CONTRAST
    yaxis.major_tick_out = None
    yaxis.major_tick_in = None
    yaxis.axis_line_color = None

    return plot

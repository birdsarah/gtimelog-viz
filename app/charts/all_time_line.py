import numpy as np
from bokeh.models import (
    Plot, Line, ColumnDataSource, DataRange1d,
    LinearAxis, BasicTicker,
    DatetimeAxis, DatetimeTicker, DatetimeTickFormatter,
    BoxZoomTool, PanTool, ResetTool, WheelZoomTool,
    Grid
)
from bokeh import palettes


def get_plot(raw):
    # Build a dictionary of frames - one for each category
    activities = list(raw.activity.unique())
    activities.remove('start')
    activities.remove('talk')
    start_df = raw[raw.activity == 'start']
    nan_df = start_df.copy()
    nan_df['delta'] = np.NaN
    nan_df['activity'] = '_'

    dfs = {}

    for activity in activities:
        activity_df = raw[raw.activity == activity]

        # Add in the start rows with 0 deltas and do cumsum
        activity_df = activity_df.append(start_df)
        activity_df.sort('timestamp', inplace=True)
        activity_df['cumsum'] = np.cumsum(activity_df.groupby(activity_df.timestamp.dt.date)['delta'])
        activity_df['cumsum_hrs'] = activity_df['cumsum'].dt.seconds / (60 * 60)

        # Add in the nan rows so bokeh can plobt
        activity_df = activity_df.append(nan_df)
        activity_df.sort(['timestamp', 'activity'], inplace=True)

        dfs[activity] = activity_df

    # Make the plot
    plot = Plot(
        x_range=DataRange1d(),
        y_range=DataRange1d(),
        background_fill='black',
        border_fill='black',
        outline_line_color=None,
        plot_width=1000,
        plot_height=300
    )

    yticker = BasicTicker(min_interval=4)
    close_ticker = DatetimeTicker(desired_num_ticks=8)
    year_ticker = DatetimeTicker(desired_num_ticks=4)
    year_ticks = DatetimeTickFormatter(
        formats={
            'years': ["%Y"],
            'months': ["%Y"],
            'days': ["%Y"],
            'hours': ["%Y"]
        }
    )
    close_ticks = DatetimeTickFormatter(
        formats={
            'years': ["%b"],
            'months': ["%b"],
            'days': ["%a %d %b"],
            'hours': ["%I%p %d %b"]
        }
    )

    axis_properties = dict(
        major_label_text_color='white',
    )
    plot.add_layout(LinearAxis(ticker=yticker, **axis_properties), 'left')
    plot.add_layout(DatetimeAxis(formatter=close_ticks, ticker=close_ticker, **axis_properties), 'below')
    plot.add_layout(DatetimeAxis(formatter=year_ticks, ticker=year_ticker, **axis_properties), 'below')
    plot.add_layout(Grid(dimension=1, ticker=yticker, grid_line_alpha=0.3))

    #tool_opts = dict(dimensions=['width'])
    #plot.add_tools(
    #    BoxZoomTool(**tool_opts),
    #    WheelZoomTool(**tool_opts),
    #    PanTool(**tool_opts),
    #    ResetTool(),

    #)

    palette = getattr(palettes, 'Spectral%s' % len(activities))

    for i, activity in enumerate(activities):
        frame = dfs[activity][['cumsum_hrs', 'timestamp']]
        source = ColumnDataSource(frame)
        line = Line(
            line_color=palette[i],
            line_join='round', line_cap='round', line_width=5, line_alpha=0.75,
            x='timestamp', y='cumsum_hrs'
        )
        plot.add_glyph(source, line)

    return plot

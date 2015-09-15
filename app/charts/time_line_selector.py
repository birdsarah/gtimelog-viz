import datetime

import numpy as np

from bokeh.models import (
    Plot, Line, ColumnDataSource, Range1d,
    LinearAxis, BasicTicker,
    DatetimeAxis, DatetimeTicker, DatetimeTickFormatter,
    PanTool, ResetTool, WheelZoomTool,
    Grid, Quad, CustomJS
)

from .chart_utils import get_palette
from .constants import COLOR_PRIMARY, COLOR_PRIMARY_CONTRAST

AXIS_PROPERTIES = dict(
    major_label_text_color=COLOR_PRIMARY_CONTRAST,
    axis_line_color=COLOR_PRIMARY,
    major_tick_line_color=COLOR_PRIMARY,
    minor_tick_line_color=COLOR_PRIMARY,
)


def get_sources_and_categories(raw):
    parent_activities = list(raw.parent_activity.unique())
    parent_activities.remove('Start')

    start_df = raw[raw.activity == 'start']
    nan_df = start_df.copy()
    nan_df['delta'] = np.NaN
    nan_df['activity'] = '_'

    dfs = {}

    # Build a dictionary of frames - one for each category
    for parent_activity in parent_activities:
        activity_df = raw[raw.parent_activity == parent_activity]

        # Add in the start rows with 0 deltas and do cumsum
        activity_df = activity_df.append(start_df)
        activity_df.sort('timestamp', inplace=True)
        activity_df['cumsum'] = np.cumsum(activity_df.groupby(activity_df.timestamp.dt.date)['delta'])
        activity_df['cumsum_hrs'] = activity_df['cumsum'].dt.seconds / (60 * 60)

        # Add in the nan rows so bokeh can plobt
        activity_df = activity_df.append(nan_df)
        activity_df.sort(['timestamp', 'activity'], inplace=True)

        dfs[parent_activity] = ColumnDataSource(activity_df[['cumsum_hrs', 'timestamp']])

    return dfs, parent_activities


def _make_base_plot(dfs, activities, x_range, plot_width=900):
    plot = Plot(
        x_range=x_range,
        y_range=Range1d(0, 11),
        outline_line_color=None,
        background_fill=COLOR_PRIMARY,
        border_fill=COLOR_PRIMARY,
        plot_width=plot_width,
        plot_height=150,
        min_border_top=0,
        toolbar_location=None,
    )

    yticker = BasicTicker(min_interval=3)
    close_ticker = DatetimeTicker(desired_num_ticks=8)
    close_ticks = DatetimeTickFormatter(
        formats={
            'years': ["%b"],
            'months': ["%b"],
            'days': ["%a %d %b"],
            'hours': ["%I%p %d %b"]
        }
    )

    plot.add_layout(LinearAxis(ticker=yticker, **AXIS_PROPERTIES), 'left')
    plot.add_layout(DatetimeAxis(formatter=close_ticks, ticker=close_ticker, **AXIS_PROPERTIES), 'below')
    plot.add_layout(Grid(dimension=1, ticker=yticker, grid_line_alpha=0.3))

    palette = get_palette(activities)

    for i, activity in enumerate(activities):
        source = dfs[activity]
        line = Line(
            line_color=palette[i],
            line_join='round', line_cap='round', line_width=5, line_alpha=0.75,
            x='timestamp', y='cumsum_hrs'
        )
        plot.add_glyph(source, line)

    return plot


def get_plot(raw, today):

    dfs, cats = get_sources_and_categories(raw)

    # Some times

    first_day = raw.loc[0, 'timestamp']
    one_week_ago = today - datetime.timedelta(weeks=1)
    two_weeks_ago = today - datetime.timedelta(weeks=2)
    one_week_forward = today + datetime.timedelta(weeks=1)

    # The ranges
    all_range = Range1d(start=first_day, end=today)
    month_range = Range1d(start=two_weeks_ago, end=one_week_forward)
    week_range = Range1d(start=one_week_ago, end=today)

    # Selection indicators
    highlight = Quad(
        left='start', right='end', bottom=0, top=12,
        fill_color='white', line_color=COLOR_PRIMARY_CONTRAST, fill_alpha=0.2,
    )
    lowlight = Quad(
        left='start', right='end', bottom=0, top=12,
        fill_color=COLOR_PRIMARY, line_color=COLOR_PRIMARY_CONTRAST, fill_alpha=0.5,
    )

    # Make the complete timeline plot
    all_plot = _make_base_plot(dfs, cats, all_range)
    detail_selection_source = ColumnDataSource({
        'start': [all_range.start, month_range.end],
        'end': [month_range.start, all_range.end]
    })
    all_plot.add_glyph(detail_selection_source, lowlight)
    # add a second axis to all_layout plot for presentation
    year_ticker = DatetimeTicker(desired_num_ticks=4)
    year_ticks = DatetimeTickFormatter(
        formats={
            'years': ["%Y"],
            'months': ["%Y"],
            'days': ["%Y"],
            'hours': ["%Y"]
        }
    )
    all_plot.add_layout(
        DatetimeAxis(formatter=year_ticks, ticker=year_ticker, **AXIS_PROPERTIES),
        'below'
    )

    # Make the detail plot
    detail_plot = _make_base_plot(dfs, cats, month_range)
    detail_plot.add_tools(PanTool(dimensions=['width']))
    detail_plot.add_tools(WheelZoomTool(dimensions=['width']))
    detail_plot.add_tools(ResetTool())

    week_selection_source = ColumnDataSource({'start': [week_range.start], 'end': [week_range.end]})
    detail_plot.add_glyph(week_selection_source, highlight)

    detail_code = """
        // Update the month selection box on the all_data plot when month pans
        var detail_selection_data = detail_selection_source.get('data');
        var detail_start = cb_obj.get('frame').get('x_range').get('start');
        var detail_end = cb_obj.get('frame').get('x_range').get('end');
        new_detail_selection = {
            'start': [detail_selection_data['start'][0], detail_end],
            'end': [detail_start, detail_selection_data['end'][1]]
        };
        detail_selection_source.set('data', new_detail_selection);

        // Always make sure the week highlight box on detail is visible and centered
        var x = moment.duration(detail_end - detail_start).asWeeks() / 2.4;
        var start = moment(detail_start);

        var week_end = start.add(x, 'weeks').format('x');
        $("#one_week_before").text(start.format('ddd, DD MMM YYYY'));
        var newStart = start.format('YYYY-MM-DD');
        var week_start = start.add(6, 'days').format('x');
        $("#today").text(start.format('ddd, DD MMM YYYY'));

        new_week_selection = {
            'start': [week_start, ],
            'end': [week_end, ]
        };
        week_selection_source.set('data', new_week_selection);

        var url = '/timesheet/?start=' + newStart;
        $("#timesheet_submit").attr('href', url).addClass("mdl-button--colored");
    """

    detail_xrange_callback = CustomJS(args={}, code=detail_code)
    detail_xrange_callback.args['detail_selection_source'] = detail_selection_source
    detail_xrange_callback.args['week_selection_source'] = week_selection_source
    detail_plot.x_range.callback = detail_xrange_callback

    return all_plot, detail_plot

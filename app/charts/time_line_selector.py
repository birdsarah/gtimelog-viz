import datetime

import numpy as np

from bokeh.models import (
    Plot, Line, ColumnDataSource, Range1d,
    LinearAxis, BasicTicker,
    DatetimeAxis, DatetimeTicker, DatetimeTickFormatter,
    PanTool, ResetTool, WheelZoomTool,
    Grid, Quad, Callback
)

from .chart_utils import get_palette


def get_sources_and_categories(raw):
    parent_activities = list(raw.parent_activity.unique())
    parent_activities.remove('Start')
    palette = get_palette(parent_activities)

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
        plot_width=plot_width,
        plot_height=150,
        toolbar_location=None,
        min_border_top=0,
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

    axis_properties = dict(
        #major_label_text_color='white',
    )
    plot.add_layout(LinearAxis(ticker=yticker, **axis_properties), 'left')
    plot.add_layout(DatetimeAxis(formatter=close_ticks, ticker=close_ticker, **axis_properties), 'below')
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
        fill_color='#3F51B5', line_color='white', fill_alpha=0.2,
    )
    lowlight = Quad(
        left='start', right='end', bottom=0, top=12,
        fill_color='black', line_color='white', fill_alpha=0.5,
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
    all_plot.add_layout(DatetimeAxis(formatter=year_ticks, ticker=year_ticker), 'below')


    # Make the detail plot
    detail_plot = _make_base_plot(dfs, cats, month_range)
    detail_plot.add_tools(PanTool(dimensions=['width']))
    detail_plot.add_tools(WheelZoomTool(dimensions=['width']))

    week_selection_source = ColumnDataSource({'start': [week_range.start], 'end': [week_range.end]})
    detail_plot.add_glyph(week_selection_source, highlight)

    detail_code = """
        // Update the month selection box on the all_data plot when month pans
        var detail_selection_data = detail_selection_source.get('data');
        var detail_start = cb_obj.get('frame').get('x_range').get('start');
        var detail_end = cb_obj.get('frame').get('x_range').get('end');
        detail_selection_data['start'][1] = detail_end;
        detail_selection_data['end'][0] = detail_start;
        detail_selection_source.trigger('change');


        // Always make sure the week highlight box on detail is visible and centered
        var week_selection_data = week_selection_source.get('data');

        var x = moment.duration(detail_end - detail_start).asWeeks() / 2.4
        var start = moment(detail_start);

        var week_end = start.add(x, 'weeks').format('x');
        $("#one_week_before").text(start.format('ddd, DD MMM YYYY'));
        var newStart = start.format('YYYY-MM-DD');
        var week_start = start.add(1, 'weeks').format('x');
        $("#today").text(start.format('ddd, DD MMM YYYY'));

        week_selection_data['start'] = [week_start];
        week_selection_data['end'] = [week_end];
        week_selection_source.trigger('change');

        var url = '/timesheet/?start=' + newStart;
        $("#timesheet_submit").attr('href', url);
        // TODO - mark timesheet as needing updating!!
    """

    detail_xrange_callback = Callback(args={}, code=detail_code)
    detail_xrange_callback.args['detail_selection_source'] = detail_selection_source
    detail_xrange_callback.args['week_selection_source'] = week_selection_source
    detail_plot.x_range.callback = detail_xrange_callback

    return all_plot, detail_plot

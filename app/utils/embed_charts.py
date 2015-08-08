import datetime

from flask import render_template

from bokeh import embed

from charts.today_summary import get_plot as today_summary_get_plot
from charts.time_line_selector import get_plot as time_line_selector_get_plot
from charts.time_log import get_plot as time_log_get_plot
from charts.timesheet_for_selected_week import get_timesheet

from .process_gtimelog import get_work_df, add_processed_columns, get_today


def assemble(today):

    work_df = get_work_df()
    df = add_processed_columns(work_df)
    today_df = get_today(today, df.copy())

    all_time_line, detail_time_line = time_line_selector_get_plot(df.copy(), today)
    time_log = time_log_get_plot(df.copy(), today)
    plots = {
        'all_time_line': all_time_line,
        'detail_time_line': detail_time_line,
        'time_log': time_log,
    }
    today_categories, today_plots, today_tables = today_summary_get_plot(today_df)
    plots.update(today_plots)

    script, plot_dicts = embed.components(plots, wrap_script=False, wrap_plot_info=False)
    plot_ids = []
    divs = {}
    div_string = '<div class="plotdiv" id="%s"></div>'
    for key, plot_dict in plot_dicts.items():
        plot_ids.append(plot_dict['modelid'])
        divs[key] = div_string % plot_dict['elementid'][1:]  # Need to remove the preceding #

    one_week_before = today - datetime.timedelta(days=6)
    weekly_timesheet = get_timesheet(df.copy(), one_week_before, today)

    return render_template(
        'minimal.html',
        today=today,
        script=script,
        divs=divs,
        plot_ids=plot_ids,
        today_categories=today_categories,
        today_tables=today_tables,
        one_week_before=one_week_before,
        weekly_timesheet=weekly_timesheet,
    )


def assemble_timesheet(start, end):
    df = add_processed_columns(get_work_df())
    weekly_timesheet = get_timesheet(df, start, end)
    return render_template(
        'timesheet.html',
        today=end,
        one_week_before=start,
        weekly_timesheet=weekly_timesheet
    )

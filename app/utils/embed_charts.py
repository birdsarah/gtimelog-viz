import datetime

from flask import render_template

from .timesheet_for_selected_week import get_timesheet
from .process_gtimelog import get_work_df, add_processed_columns


def assemble(today):
    work_df = get_work_df()
    df = add_processed_columns(work_df)
    one_week_before = today - datetime.timedelta(days=6)
    weekly_timesheet = get_timesheet(df, one_week_before, today)

    return render_template(
        'main.html',
        today=today,
        one_week_before=one_week_before,
        weekly_timesheet=weekly_timesheet,
    )


def assemble_timesheet(start, end):
    df = add_processed_columns(get_work_df())
    weekly_timesheet = get_timesheet(df, start, end)
    return render_template(
        'main.html',
        today=end,
        one_week_before=start,
        weekly_timesheet=weekly_timesheet
    )

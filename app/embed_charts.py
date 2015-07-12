from flask import render_template

from bokeh.embed import components

from process_gtimelog import keep_top_level_cats_only
from charts.all_time_line import get_plot


def assemble(raw):
    gt_df = keep_top_level_cats_only(raw)
    all_time_line = get_plot(gt_df)
    script, div = components(all_time_line)
    return render_template('main.html', script=script, div=div)

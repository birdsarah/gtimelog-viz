from flask import render_template

from bokeh import embed

from process_gtimelog import get_work_df
from process_gtimelog import add_parent_activity
from charts.all_time_line import get_plot as all_time_line_get_plot
from charts.today_summary import get_plot as today_summary_get_plot


# Monkey patch method called by components so it returns raw js
# not js wrapped in script tags and Bokeh function.
def _new_component_pair(all_models, plots, divs):
    js = embed.PLOT_JS.render(
        all_models=embed.serialize_json(all_models),
        plots=plots
    )
    return js, divs
embed._component_pair = _new_component_pair


def assemble():
    all_time_line = all_time_line_get_plot(add_parent_activity(get_work_df()))
    today_summary = today_summary_get_plot(get_work_df())

    plots = {
        'all_time_line': all_time_line,
        'today_summary': today_summary
    }

    plot_ids = [plot.ref.get('id') for plot in plots.values()]


    script, divs = embed.components(plots)
    return render_template('main.html', script=script, divs=divs, plot_ids=plot_ids)

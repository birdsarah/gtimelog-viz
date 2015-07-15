from flask import render_template

from bokeh import embed

from charts.all_time_line import get_plot as all_time_line_get_plot
from charts.today_yesterday_bar import get_plot as today_yesterday_bar_get_plot
from charts.today_summary import get_plot as today_summary_get_plot

from .process_gtimelog import get_work_df
from .process_gtimelog import add_processed_columns


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
    df = add_processed_columns(get_work_df())
    all_time_line = all_time_line_get_plot(df.copy())
    #today_yesterday_bar = today_yesterday_bar_get_plot(df.copy())
    today_categories, today_plots = today_summary_get_plot(df.copy())

    plots = {
        'all_time_line': all_time_line,
    }

    plot_ids = [plot.ref.get('id') for plot in plots.values()]
    today_plot_ids = [plot.ref.get('id') for plot in today_plots.values()]
    plot_ids += today_plot_ids

    today_script, today_divs = embed.components(today_plots)
    other_script, other_divs = embed.components(plots)
    return render_template(
        'minimal.html',
        other_script=other_script,
        other_divs=other_divs,
        plot_ids=plot_ids,
        today_categories=today_categories,
        today_script=today_script,
        today_divs=today_divs,
    )

from flask import render_template

from bokeh import embed

from process_gtimelog import keep_top_level_cats_only
from charts.all_time_line import get_plot


# Monkey patch method called by components so it returns raw js
# not js wrapped in script tags and Bokeh function.
def _new_component_pair(all_models, plots, divs):
    js = embed.PLOT_JS.render(
        all_models=embed.serialize_json(all_models),
        plots=plots
    )
    return js, divs
embed._component_pair = _new_component_pair


def assemble(raw):
    gt_df = keep_top_level_cats_only(raw)
    all_time_line = get_plot(gt_df)

    plot_ids = [plot.ref.get('id') for plot in [all_time_line]]

    script, div = embed.components(all_time_line)
    return render_template('main.html', script=script, div=div, plot_ids=plot_ids)

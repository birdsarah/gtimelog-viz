// Need plot_ids in context
// plot_ids is a list of all the bokeh index ids

function resize_plots() {
  {% for plot_id in plot_ids %}
      var bokeh_obj = Bokeh.index["{{ plot_id }}"];
      var div_id = bokeh_obj.el.id;
      var div = $("#" + div_id);
      var div_width = div.width();
      var plot = div.find('.bk-canvas-wrapper');
      var cur_width = plot.width();
      var cur_height = plot.height();
      var aspect_ratio = cur_width / cur_height;

      var plot_width = Math.max(div_width, 200);
      var plot_height = parseInt(plot_width / aspect_ratio);
      var plot_height = Math.max(plot_height, 100);

      bokeh_obj.model.set('plot_width', plot_width);
      bokeh_obj.model.set('plot_height', plot_height);
  {% endfor %}
}

// Attach resize_plots to window resize event
$(window).resize(resize_plots);

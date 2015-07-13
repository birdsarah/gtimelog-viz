// Need plot_ids in context
// plot_ids is a list of all the bokeh index ids

function resize_plots() {
  var bokeh_obj,
      div_id, 
      container, 
      container_width,
      plot,
      cur_width,
      cur_height,
      aspect_ratio,
      new_width,
      new_height;

  // Note this doesn't account for desired padding in the container

  {% for plot_id in plot_ids %}
      bokeh_obj = Bokeh.index["{{ plot_id }}"];
      div_id = bokeh_obj.el.id;
      container = $("#" + div_id).parent();
      container_width = container.width();
      plot = container.find('.bk-canvas-wrapper');
      cur_width = plot.width();
      cur_height = plot.height();
      aspect_ratio = cur_width / cur_height;

      new_width = Math.max(container_width, 200);  // We can't set it too small
      new_height = parseInt(new_width / aspect_ratio);
      new_height = Math.max(new_height, 100);  // We can't set it too small

      bokeh_obj.model.set('plot_width', new_width);
      bokeh_obj.model.set('plot_height', new_height);
  {% endfor %}
}

// Attach resize_plots to window resize event
$(window).resize(resize_plots);

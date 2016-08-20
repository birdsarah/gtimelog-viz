from bokeh import palettes


def get_palette(list_of_categories):
    n = len(list_of_categories)
    palette = palettes.Spectral11
    if hasattr(palettes, 'Spectral%s' % n):
        palette = getattr(palettes, 'Spectral%s' % n)
    return palette


def make_mdl_table(df, *args, **kwargs):
    """
    Returns html table with mdl classes
    """
    return df.to_html(classes=["mdl-data-table", "mdl-js-data-table"], **kwargs)

from bokeh import palettes


def get_palette(list_of_categories):
    n = len(list_of_categories)
    palette = palettes.Spectral11
    if hasattr(palettes, 'Spectral%s' % n):
        palette = getattr(palettes, 'Spectral%s' % n)
    return palette

# Reference

## ::: includex
    options:
        show_root_heading: false
        show_root_toc_entry: false
        docstring_section_style: list

{% for feature in get_files("docs/_features") %}

### {{feature.stem}}

{{ includex(feature) }}

{% endfor %}

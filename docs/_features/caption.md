Include a caption with included content, that is rendered as a code block via [lang][].

The caption will have a `.caption` css class applied via [`attr_list`](https://python-markdown.github.io/extensions/attr_list/). So ensure you have this markdown extension enabled in your `mkdocs.yaml`:

```
markdown_extensions:
  - attr_list
  - ...
```

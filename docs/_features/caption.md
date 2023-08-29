Include a caption with included content, that is rendered as a code block via [lang][].

The caption will have a `.caption` css class applied via [`attr_list`](https://python-markdown.github.io/extensions/attr_list/). So ensure you have this markdown extension enabled in your `mkdocs.yaml`:

```
markdown_extensions:
  - attr_list
  - ...
```

Then you can style these captions to look just like figcaptions. Here is an example for Material for MkDocs:

<!-- TODO: When includex can be nested, use the command below instead of the copy-pasted css block -->
<!-- {{ includex('docs/custom.css', start_match="center captions", end_match="}", start_offset=1) }} -->

```css
/* center captions */
.md-typeset .caption,
.md-typeset figcaption {
    /* same as material's figcaption */
    font-style: normal;
    max-width: 24rem;
    margin: 1em auto 1.5em;
    text-align: center;
    display: block;
    font-size: 0.8rem;
    /* custom */
    line-height: 1.2;
}
```

def rich_text_section_header(text):
    elements = [dict(type="text", text=text, style={"bold": True})]
    form = dict(type="rich_text_section", elements=elements)
    return form


def heading_1_header(content):
    annotations = dict(
        bold=True,
        italic=False,
        strikethrough=False,
        underline=False,
        code=False,
        color="default",
    )
    rich_text = [
        dict(
            type="text",
            text={
                "content": content,
            },
            annotations=annotations,
        )
    ]
    heading_1 = dict(rich_text=rich_text)
    form = dict(type="heading_1", heading_1=heading_1)
    return form

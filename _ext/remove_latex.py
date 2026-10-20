"""Remove do PDF as células de notebook marcadas com a tag `remove-latex`.

Serve para conteúdo que só funciona no site, como animações geradas com
`to_jshtml()`: no PDF elas aparecem apenas como `<IPython.core.display.HTML
object>`. A célula continua inteira na versão HTML.

Carregado como extensão local do Sphinx/Jupyter Book (ver
`sphinx.local_extensions` em _config.yml). Para usar, adicione a tag
`remove-latex` aos metadados da célula.
"""

from docutils import nodes

TAG = "tag_remove-latex"


def _remove_tagged_cells(app, doctree, docname):
    if app.builder.format != "latex":
        return
    for node in list(doctree.findall(nodes.container)):
        if TAG in node.get("classes", []):
            node.parent.remove(node)


def setup(app):
    app.connect("doctree-resolved", _remove_tagged_cells)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}

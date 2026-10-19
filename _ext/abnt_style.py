"""Estilo pybtex que aproxima as regras de referência da ABNT NBR 6023.

Cobre bem entradas do tipo @book (o único tipo usado hoje em references.bib):
autores em SOBRENOME, Nome (separados por ";", truncados em "et al." acima de
3 autores), título em negrito, edição, cidade: editora, ano. Outros tipos de
entrada (@article, @misc, etc.) herdam a formatação do estilo "unsrt", mas já
usam a formatação de nomes e a ordenação alfabética da ABNT.

Carregado como extensão local do Sphinx/Jupyter Book (ver `sphinx.local_extensions`
em _config.yml). Depois de carregado, use `:style: abnt` na diretiva
`{bibliography}`.
"""

from pybtex.plugin import register_plugin
from pybtex.style.formatting import toplevel
from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.names import BaseNameStyle, name_part
from pybtex.style.template import FieldIsMissing, field, join, node, optional, sentence, tag


class ABNTNameStyle(BaseNameStyle):
    """SOBRENOME, Nome do Meio — sobrenome em caixa alta, como pede a ABNT."""

    def format(self, person, abbr=False):
        surname_parts = [
            piece.upper()
            for piece in (
                person.rich_prelast_names
                + person.rich_last_names
                + person.rich_lineage_names
            )
        ]
        surname = name_part[surname_parts]
        given_names = name_part(before=", ", abbr=abbr)[
            person.rich_first_names + person.rich_middle_names
        ]
        return join[surname, given_names]


@node
def abnt_authors(children, context, role):
    """Autores separados por ";"; truncado em "et al." acima de 3 autores."""
    if children:
        raise ValueError(children)
    entry = context["entry"]
    if role not in entry.persons:
        raise FieldIsMissing(role, entry)
    persons = entry.persons[role]
    style = context["style"]
    if len(persons) > 3:
        first = style.format_name(persons[0], style.abbreviate_names)
        return join(sep=" ")[first, "et al."].format_data(context)
    formatted = [style.format_name(p, style.abbreviate_names) for p in persons]
    return join(sep="; ")[formatted].format_data(context)


class ABNTStyle(UnsrtStyle):
    """Aproximação das regras da ABNT NBR 6023, com foco em referências de livros."""

    default_sorting_style = "author_year_title"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format_name = ABNTNameStyle().format

    def format_names(self, role, as_sentence=True):
        formatted = abnt_authors(role)
        if as_sentence:
            return sentence[formatted]
        return formatted

    def get_book_template(self, e):
        edition = optional[join(sep="")[field("edition"), ". ed."]]
        place_publisher_year = sentence(add_period=True, sep=": ")[
            field("address"),
            join(sep=", ")[field("publisher"), field("year")],
        ]
        return toplevel[
            self.format_author_or_editor(e),
            sentence(add_period=True)[tag("b")[field("title")]],
            join(sep=" ")[edition, place_publisher_year],
        ]


def setup(app):
    register_plugin("pybtex.style.formatting", "abnt", ABNTStyle, force=True)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}

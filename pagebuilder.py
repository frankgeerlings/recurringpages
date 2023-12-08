import pywikibot

SUMMARY = "Automatische aanmaak aan de hand van {{[[Sjabloon:%s|%s]]}}"

class PageFromTemplate:
    """
    In iedere template-gebaseerde aanmaak is in de titel te zien op welk
    sjabloon het is gebaseerd:

    >>> PageFromTemplate("Titel", "Tekst", "Sjabloonzandbak").summary
    'Automatische aanmaak aan de hand van {{[[Sjabloon:Sjabloonzandbak|Sjabloonzandbak]]}}'
    """

    def __init__(self, title, text, template) -> None:
        self.title = title
        self.text = text
        self.template = template
        self.summary = SUMMARY % (template, template)

    def treat_page(self, page: pywikibot.Page) -> dict:
        if page.exists():
            print(f"Ik heb {self.title} overgeslagen want deze bestond al")
        else:
            page.text = self.text
            page.save(summary=self.summary, botflag=True)

        summary_row = {
            "interval": 'maandelijks',
            "page": f"[[{self.title}]]",
            "template": "{{tl|%s}}" % self.template,
        }

        return summary_row


from datetime import datetime
from genericpath import exists
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
        self.summary = SUMMARY % (template, template)

class DeceasedThisMonth(PageFromTemplate):
    """
    De titel bevat het jaartal en de maand:

    >>> DeceasedThisMonth(datetime(2023,12,4)).title
    'Lijst van personen overleden in december 2023'

    De maand en het jaartal worden als argumenten aan het te
    substitueren sjabloon doorgegeven, en verder niets.

    Zo kunnen wijzigingen in de code tot een minimum beperkt worden, de
    meeste aanpassingen kunnen op de wiki worden uitgevoerd:

    >>> DeceasedThisMonth(datetime(2011,12,4)).text
    '{{subst:Basis voor lijst van personen overleden in maand|2011|12}}'
    """

    def __init__(self, now):
        TEMPLATE = "Basis voor lijst van personen overleden in maand"

        maand = ["januari", "februari", "maart", "april", "mei", "juni",
                 "juli", "augustus", "september", "oktober", "november",
                 "december"][now.month - 1]

        pagename = f"Lijst van personen overleden in {maand} {now.year}"
        text = "{{subst:%s|%d|%d}}" % (TEMPLATE, now.year, now.month)

        super().__init__(pagename, text, TEMPLATE)

def main():
    template = DeceasedThisMonth(datetime.now())

    site = pywikibot.Site("nl", "wikipedia")
    page = pywikibot.Page(site, template.title)
    
    if page.exists():
        print(f"Niets gedaan want de pagina {template.title} bestond al")
    else:
        page.text = template.text
        page.save(summary=template.summary, botflag=True)

if __name__ == '__main__':
    main()
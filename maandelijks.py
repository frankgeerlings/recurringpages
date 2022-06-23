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

class Samenvoegen(PageFromTemplate):
    """
    De titel bevat het jaartal en de maand en verder niets:
    >>> Samenvoegen(datetime(2023,12,4)).title
    'Wikipedia:Samenvoegen/202312'

    Enkelcijferige maanden krijgen een voorloopnul:
    >>> Samenvoegen(datetime(2023,1,4)).title
    'Wikipedia:Samenvoegen/202301'

    De inhoud is simpelweg het gesubstitueerde sjabloon zonder argumenten:
    >>> Samenvoegen(datetime(1234,5,6)).text
    '{{subst:Samenvoegen nieuwe maand/Preload}}'
    """
    def __init__(self, now):
        TEMPLATE = "Samenvoegen nieuwe maand/Preload"

        pagename = f"Wikipedia:Samenvoegen/{now.year}{now.month:02d}"
        text = "{{subst:%s}}" % TEMPLATE

        super().__init__(pagename, text, TEMPLATE)

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

def handle_template(site, template):
    page = pywikibot.Page(site, template.title)
    
    if page.exists():
        print(f"Ik heb {template.title} overgeslagen want deze bestond al")
    else:
        page.text = template.text
        page.save(summary=template.summary, botflag=True)

def main():
    now = datetime.now()

    templates = [
        DeceasedThisMonth(now),
        Samenvoegen(now),
    ]

    site = pywikibot.Site("nl", "wikipedia")

    for template in templates:
        handle_template(site, template)

if __name__ == '__main__':
    main()
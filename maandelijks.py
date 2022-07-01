from datetime import datetime
from wikitable import Table
from genericpath import exists
import pywikibot

SUMMARY = "Automatische aanmaak aan de hand van {{[[Sjabloon:%s|%s]]}}"
SUMMARY_PAGENAME = "Gebruiker:Herhaalbot/Overzicht"

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


    De inhoud is simpelweg het gesubstitueerde sjabloon zonder argumenten:
    >>> DeceasedThisMonth(datetime(2011,12,4)).text
    '{{subst:Basis voor lijst van personen overleden in maand}}'
    """

    def __init__(self, now):
        TEMPLATE = "Basis voor lijst van personen overleden in maand"

        maand = ["januari", "februari", "maart", "april", "mei", "juni",
                 "juli", "augustus", "september", "oktober", "november",
                 "december"][now.month - 1]

        pagename = f"Lijst van personen overleden in {maand} {now.year}"
        text = "{{subst:%s}}" % TEMPLATE

        super().__init__(pagename, text, TEMPLATE)

def handle_template(site, template):
    page = pywikibot.Page(site, template.title)

    summary_row = {
        "interval": 'maandelijks',
        "page": f"[[{template.title}]]",
        "template": "{{tl|%s}}" % template.template,
    }
    
    if page.exists():
        print(f"Ik heb {template.title} overgeslagen want deze bestond al")
    else:
        page.text = template.text
        page.save(summary=template.summary, botflag=True)

    return summary_row

def publish_summary(site: pywikibot.Site, pagename: str, summary):
    CAPTION = "Overzicht van door Herhaalbot aangemaakte pagina's"

    header_row = {
        "interval": "Aanmaakfrequentie",
        "page": "Meest recente in de reeks",
        "template": "Op basis van sjabloon",
    }

    table = Table(header_row, summary, caption=CAPTION)

    page = pywikibot.Page(site, pagename)
    page.text = table.wikitext()
    page.save(summary=CAPTION, botflag=True)

def main():
    now = datetime.now()

    print(f"Maandelijkse run van {now.isoformat()}")

    templates = [
        DeceasedThisMonth(now),
        Samenvoegen(now),
    ]

    summary_table = []

    site = pywikibot.Site("nl", "wikipedia")

    for template in templates:
        try:
            summary_table.append(handle_template(site, template))
        except BaseException as err:
            print(f"Exception trad op: {err}, {type(err)}")

    publish_summary(site, SUMMARY_PAGENAME, summary_table)

if __name__ == '__main__':
    main()
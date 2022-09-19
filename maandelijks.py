from datetime import datetime
import inspect
from dateutil.relativedelta import relativedelta
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

class SamenvoegenFooter:
    def __init__(self, dateforhandling) -> None:
        self.description = f"''Zie broncode vanaf regel {inspect.getframeinfo(inspect.currentframe()).lineno}''"

        current_month = self.__formatdate(dateforhandling)
        next_month = self.__formatdate(dateforhandling + relativedelta(months=1))
        self.summary = "Automatisch een nieuwe maand"
        self.title = "Wikipedia:Samenvoegen"

        self.__replace_footer = lambda text: text.replace("{{/footer|%s}}" % current_month, "{{/%s}}\n{{/footer|%s}}" % (current_month, next_month))

    @staticmethod
    def __formatdate(date: datetime) -> str:
        return f"{date.year}{date.month:02d}"

    def treat_page(self, page: pywikibot.Page) -> dict:
        if not page.exists():
            print(f'Ik kon {self.title} niet aanpassen want deze bestaat niet')
            return None
        else:
            original = page.text
            page.text = self.__replace_footer(page.text)

            if(page.text == original):
                print(f'Geen aanpassingen in {self.title} dus niet opgeslagen')
                return None

            page.save(summary=self.summary, botflag=True)

        summary_row = {
            "interval": 'maandelijks',
            "page": f"[[{self.title}]]",
            "template": self.description
        }

        return summary_row

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
    def __init__(self, dateforhandling):
        TEMPLATE = "Samenvoegen nieuwe maand/Preload"

        pagename = f"Wikipedia:Samenvoegen/{dateforhandling.year}{dateforhandling.month:02d}"
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

    def __init__(self, dateforhandling):
        TEMPLATE = "Basis voor lijst van personen overleden in maand"

        maand = ["januari", "februari", "maart", "april", "mei", "juni",
                 "juli", "augustus", "september", "oktober", "november",
                 "december"][dateforhandling.month - 1]

        pagename = f"Lijst van personen overleden in {maand} {dateforhandling.year}"
        text = "{{subst:%s}}" % TEMPLATE

        super().__init__(pagename, text, TEMPLATE)

class ThisMonth(PageFromTemplate):
    def __init__(self, dateforhandling):
        TEMPLATE = "Basis voor maand jaar"

        maand = ["Januari", "Februari", "Maart", "April", "Mei", "Juni",
                 "Juli", "Augustus", "September", "Oktober", "November",
                 "December"][dateforhandling.month - 1]

        pagename = f"{maand} {dateforhandling.year}"
        text = "{{subst:%s}}" % TEMPLATE

        super().__init__(pagename, text, TEMPLATE)

def handle_template(site, template: PageFromTemplate) -> dict:
    page = pywikibot.Page(site, template.title)

    summary_row = template.treat_page(page)

    return summary_row

def publish_summary(site: pywikibot.Site, pagename: str, summary):
    CAPTION = "Overzicht van door Herhaalbot aangemaakte of aangepaste pagina's"

    header_row = {
        "interval": "Herhalingsinterval",
        "page": "Meest recente in de reeks",
        "template": "Op basis van sjabloon",
    }

    table = Table(header_row, list(filter(None, summary)), caption=CAPTION)

    page = pywikibot.Page(site, pagename)
    page.text = table.wikitext()
    page.save(summary=CAPTION, botflag=True)

def main():
    now = datetime.now()
    dateforhandling = now + relativedelta(days=1)
    if now.month == dateforhandling.month:
      print(f"{now.isoformat()} is niet de laatste dag van de maand")
      exit()

    print(f"Maandelijkse run van {now.isoformat()}")

    templates = [
        DeceasedThisMonth(dateforhandling),
        Samenvoegen(dateforhandling),
        SamenvoegenFooter(dateforhandling),
        ThisMonth(dateforhandling),
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

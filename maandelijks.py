from datetime import datetime
import inspect
from dateutil.relativedelta import relativedelta
from wikitable import Table
from genericpath import exists
import pywikibot
import traceback
from pagebuilder import PageFromTemplate
from tasks import find_tasks

SUMMARY_PAGENAME = "Gebruiker:Herhaalbot/Overzicht"
TASKS_PAGENAME = "Gebruiker:Herhaalbot/Opdrachten"

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

    site = pywikibot.Site("nl", "wikipedia")
    tasks_page = pywikibot.Page(site, TASKS_PAGENAME)

    # Doe alle gevonden opdrachten plus de hardcoded opdracht (die heeft custom code)
    templates = list(find_tasks(site, tasks_page)) + [ SamenvoegenFooter(dateforhandling) ]

    summary_table = []

    for template in templates:
        try:
            summary_table.append(handle_template(site, template))
        except BaseException as err:
            trace = traceback.format_exc()
            print(f"Exception trad op: {err}, {type(err)}\n{trace}")

    publish_summary(site, SUMMARY_PAGENAME, summary_table)

if __name__ == '__main__':
    main()

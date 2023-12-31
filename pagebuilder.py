from datetime import datetime
import pywikibot

SUMMARY = "Automatische aanmaak aan de hand van {{[[Sjabloon:%s|%s]]}}"

class PageFromTemplate:
    """
    In iedere template-gebaseerde aanmaak is in de titel te zien op welk
    sjabloon het is gebaseerd:

    >>> PageFromTemplate("Titel", "Tekst", "Sjabloonzandbak").summary
    'Automatische aanmaak aan de hand van {{[[Sjabloon:Sjabloonzandbak|Sjabloonzandbak]]}}'
    """

    def __init__(self, title, text, template, interval) -> None:
        self.title = title
        self.text = text
        self.template = template
        self.interval = interval
        self.summary = SUMMARY % (template, template)

    def treat_page(self, page: pywikibot.Page, dateforhandling: datetime) -> dict:
        if dateforhandling.month > 1 and self.interval == "jaarlijks":
            print(f"Ik heb {self.title} overgeslagen want het is niet januari")
            self.interval = f"<s>{self.interval}</s>"
            title_in_summary = f"<s>[[{self.title}]]</s> ''(alleen januari)''"
        elif page.exists():
            print(f"Ik heb {self.title} overgeslagen want deze bestond al")
            title_in_summary = f"<s>[[{self.title}]]</s> ''(bestond al)''"
        elif self.interval == "maandelijks":
            page.text = self.text
            page.save(summary=self.summary, botflag=True)
            title_in_summary = f"[[{self.title}]]"
        else:
            print(f"Ik heb {self.title} overgeslagen want ik herken het interval niet")
            self.interval = f"<s>{self.interval}</s> ''(onbekend)''"
            title_in_summary = f"<s>[[{self.title}]]</s>"

        summary_row = {
            "interval": self.interval,
            "page": title_in_summary,
            "template": "{{tl|%s}}" % self.template,
        }

        return summary_row


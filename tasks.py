import pywikibot
import mwparserfromhell
from pprint import pprint
import re
from pagebuilder import PageFromTemplate

def find_tasks(site, page):
    code = mwparserfromhell.parse(page.text)
    rows = code.filter_tags(matches = lambda node: node.tag == "td")

    for interval_col, title_col, template_col in [tuple(rows[i:i+3]) for i in range(0, len(rows), 3)]:
        title_mwcode = (title_col.contents.strip())
        title = site.expand_text(title_mwcode)

        tl = template_col.contents.strip()
        template = re.match(r'{{(?:tl\|)?(.*?)}}', tl).groups()[0]

        yield PageFromTemplate(title, '{{subst:%s}}' % template, template)

        # Nog niet geimplementeerd, want niet essentieel. Omdat de jaarlijkse pagina's vanaf januari
        # bestaan en al bestaande pagina's niet worden overschreven, gebeurt er van februari tot
        # december niets ergs.

        # match interval_col.contents.strip():
        #     case "maandelijks":

        #     case "jaarlijks":

def main():
    # Dit is vooral voor debugging
    site = pywikibot.Site("nl", "wikipedia")
    page = pywikibot.Page(site, "Gebruiker:Herhaalbot/Opdrachten")

    pprint(list(find_tasks(site, page)))

if __name__ == '__main__':
    main()
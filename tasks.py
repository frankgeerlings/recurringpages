import pywikibot
from pprint import pprint
import re
from pagebuilder import PageFromTemplate

def find_tasks(site, page):
    lines = page.text.splitlines()
    rows = [(lines[i + 1][1:].strip(), lines[i + 2][1:].strip(), lines[i + 3][1:].strip()) for i in range(len(lines)) if lines[i] == '|-']

    for interval, title_mwcode, tl in rows:
        title = site.expand_text(title_mwcode)
        template = re.match(r'{{(?:tl\|)?(.*?)}}', tl).groups()[0]

        yield PageFromTemplate(title, '{{subst:%s}}' % template, template, interval)

def main():
    # Dit is vooral voor debugging
    site = pywikibot.Site("nl", "wikipedia")
    page = pywikibot.Page(site, "Gebruiker:Herhaalbot/Opdrachten")

    pprint(list([vars(i) for i in find_tasks(site, page)]))

if __name__ == '__main__':
    main()
class Table:
    def __init__(self, header: dict, rows, caption = None):
        self.header = header
        self.rows = rows
        self.caption = caption

    def __row(self, prefix, columns, row):
        return ''.join([f'{prefix} {row[column]}\n' for column in columns])

    def wikitext(self):
        result = '{| class="wikitable" style="width: 100%"\n'

        "Add the caption between start and first row, if any"
        if self.caption:
            result += f'|+ {self.caption}\n'

        columns = self.header.keys()

        "Add header"
        result += self.__row('! ', columns, self.header)

        "Add all the rows, each starting with a row separator"
        result += ''.join(['|-\n' + self.__row('| ', columns, row) for row in self.rows])

        "End the table"
        result += "|}\n"

        return result
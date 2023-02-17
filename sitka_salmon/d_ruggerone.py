import os,functools,re,itertools,more_itertools,collections
import openpyxl
import pandas as pd
from sitka_salmon import config

ruggerone2018_xlsx = os.path.join(config.HARNESS, 'data', 'Ruggerone2018', 'mcf210023-sup-0001-tables1-s24.xlsx')


def get_cheaders(rows):
    """Returns the headers (and column ranges) for each sub-table
    Returns: row0, [(col0, headers), ...]
        col0:
            First column for each sub-worksheet
        headers:
            Headers for each sub-worksheet"""
    for irow,row in enumerate(rows):
        year_ixs = list(more_itertools.locate(row, lambda x: x=='Year'))
        if len(year_ixs) != 3:    # 3 sub-worksheets: pink, chinook, sockeye
            continue
        none_ixs = list(more_itertools.locate(row, lambda x: x is None))

        ranges = list(zip(year_ixs, none_ixs))
        return irow, [(i0, [x.strip() for x in row[i0:i1]]) for i0,i1 in ranges]


Table = collections.namedtuple('Table', ('title', 'species', 'description', 'df'))

speciesRE = re.compile(r'.*(Pink|Chum|Sockeye).*', flags=re.IGNORECASE)
def parse_sheet(sheet):
    rows = [row for row in sheet.iter_rows(values_only=True)]
    irow0,cheaders = get_cheaders(rows)
    tables = dict()
    for icol0,headers in cheaders:
        # Fetch the data for this sub-table
        valss = list()
        for row in rows[irow0:]:
            # Empty line is end of data
            if row[0] is None:
                break
            valss.append(row[icol0:icol0+len(headers)])

        title = rows[irow0-4][icol0].strip()    # Title
        match = speciesRE.match(title)
        species = match.group(1).strip().lower()
        df = pd.DataFrame(valss, columns=headers).set_index('Year')
        tables[species] = Table(
            title, species,
            rows[irow0-2][0].strip(),    # description
            df)

    return tables    

@functools.lru_cache()
def get_xlsx():
    return openpyxl.load_workbook(ruggerone2018_xlsx, read_only=True, data_only=True)    # data_only=True: Read values, not formulas

@functools.lru_cache()
def get_subsheets(sheet_ix):
    """Returns sheet for a workbook index"""
    xlsx = get_xlsx()
    return parse_sheet(xlsx.worksheets[sheet_ix])

_worksheets = {
    ('natural', 'mature', 'abundance'): 4,
    ('hatchery', 'mature', 'abundance'): 5,
    ('*', 'mature', 'abundance'): 6,
    ('*', 'mature', 'biomass'): 7,
    ('*', '*', 'biomass'): 8,
}
def get(born, age, measure, species):
    sheet_ix = _worksheets[(born, age, measure)]
    return get_subsheets(sheet_ix)[species]


print(get('*', 'mature', 'abundance', 'chum'))

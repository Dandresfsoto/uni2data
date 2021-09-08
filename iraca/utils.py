def autonumeric2float(valor):
    return float(valor.replace('$ ','').replace(',',''))


def col2str(valor):
    return str(valor).replace('COL$','$ ')

def pretty_datetime(datetime):
    return datetime.strftime('%d/%m/%Y %I:%M:%S %p')
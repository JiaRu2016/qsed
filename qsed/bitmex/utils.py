def calculate_td_ts(x, bar_type):
    """"2018-09-29T06:00:17.271Z -> 20180929, 617"""
    # x = '2018-09-29T06:17:34.271Z'
    # bar_type = '4h'
    
    td, sec = x.split('T')
    td = int(td.replace('-', ''))
    
    n, what = int(bar_type[:-1]), bar_type[-1]    
    h, m, s = sec[:8].split(':')
    if what == 'h':
        ts = '%02d' % (int(h) // n * n)
    elif what == 'm':
        ts = h + '%02d' % (int(m) // n * n)
    elif what == 's':
        ts = h + m + '%02d' % (int(s) // n * n)
    else:
        raise ValueError('bar_type pattern should be "\\d[h|m|s]"')
        
    return td, int(ts)


VALID_BAR_TYPE = ('1m', '5m', '1h', '1d')


def check_bar_type(bar_type):
    if bar_type not in VALID_BAR_TYPE:
        raise ValueError("bar_type must be one of %s" % VALID_BAR_TYPE)
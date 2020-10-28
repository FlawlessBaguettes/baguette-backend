import datetime
from math import floor
def prettydate(d):
    diff = datetime.datetime.utcnow() - d
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1d'
    elif diff.days > 1:
        return '{}d'.format(diff.days)
    elif s < 60:
        return '{} seconds ago'.format(s)
    elif s < 120:
        return '1m'
    elif s < 3600:
        return '{}m'.format(floor(s/60))
    elif s < 7200:
        return '1h'
    else:
        return '{}h'.format(floor(s/3600))
def interpretValue(name, value):
    """Interprets values. name should be string. Value should be list or tuple.
       Returns dictionary with fixed values."""
    # Removing units.
    if name[1:] == 'lastReading':
        fixedValue = value[1].split('*')[0]
        # lastReading needs timestamp processing.
        fixedTimestamp = converttimestamp(value[0])
        return {'name': name, 'value': fixedValue, 'timestamp': fixedTimestamp}
    else:
        fixedValue = value[0].split('*')[0]
        return {'name': name, 'value': fixedValue}

def converttimestamp(value):
    """Converts a timestamp from YYMMDDHHmmSSX to MySQL timestamp.
    'YYYY-MM-DD HH:MM:SS"""
    # TODO Interpret DST.
    return ('20' + value[0:2] + '-' + value[2:4] + '-' + value[4:6] + ' ' +
            value[6:8] + ':' + value[8:10] + ':' + value[10:12])

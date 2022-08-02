def convert(time):
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    unit = time[-1]
    if unit not in time_dict:
        return -1
    try:
        val = int(time[:-1])
    except: 
        return -1
    return val * time_dict[unit]
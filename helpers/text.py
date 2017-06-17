def truncate(string, width):
    if len(string) > width:
        string = string[:width-3] + '...'
    return string
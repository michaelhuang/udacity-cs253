def gray_style(lst):
    for n, x in enumerate(lst):
        if n % 2 == 0:
            yield x, ''
        else:
            yield x, 'gray'

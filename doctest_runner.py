if __name__ == "__main__":
    import doctest
    from home_board import calendar, nws
    results = doctest.testmod(calendar)
    results = tuple(map(sum, zip(results, doctest.testmod(nws))))
    print('{success}/{total} Tests Passing'.format(success=results[1] - results[0], total=results[1]))


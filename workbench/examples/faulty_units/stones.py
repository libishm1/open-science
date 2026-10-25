def count_in_range(lengths, lo, hi):
    return sum(1 for x in lengths if lo <= x < hi)

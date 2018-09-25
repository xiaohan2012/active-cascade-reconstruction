# profile.py

import pstats, cProfile

import si_example

cProfile.runctx("si_example.main()", globals(), locals(), "Profile.prof")

s = pstats.Stats("Profile.prof")
s.strip_dirs().sort_stats("time").print_stats()

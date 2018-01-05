import line_profiler

from demo import cp_func

profile = line_profiler.LineProfiler(cp_func)
profile.runcall(cp_func, 20)
profile.print_stats()

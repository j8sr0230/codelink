import cProfile
import pstats
from pstats import SortKey

import app

cProfile.run("app.main()", "app_stats")
p: pstats.Stats = pstats.Stats("app_stats")
p: pstats.Stats = p.strip_dirs().sort_stats(SortKey.TIME).print_stats(10)

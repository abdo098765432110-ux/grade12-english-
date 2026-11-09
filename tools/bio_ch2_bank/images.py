"""All 50 image questions, in order (figs1.py, figs2.py, figs3.py)."""
from figs1 import QUESTIONS as Q1
try:
    from figs2 import QUESTIONS as Q2
except ImportError:
    Q2 = []
try:
    from figs3 import QUESTIONS as Q3
except ImportError:
    Q3 = []
IMAGES = Q1 + Q2 + Q3

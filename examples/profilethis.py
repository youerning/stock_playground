python -m cProfile -o profile.out cProfileTest1.py
python -c "import pstats; p=pstats.Stats('profile.out'); p.sort_stats('time').print_stats()"
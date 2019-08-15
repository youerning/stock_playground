
通过cProfile优化性能
```
python -m cProfile -s cumulative -o profile.stat mybacktest.py

python -c "import pstats; p=pstats.Stats('profile.stat'); p.sort_stats('cumulative').print_stats()" > prof.stat
```
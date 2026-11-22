import json,sys,importlib.util
from pathlib import Path
H=Path(r'C:\Users\DomBa\DOM\5_Projects\Bavuso Motors\v1.0\program\tools'); OUT=H.parents[1]/'program'/'data'/'fea'
sys.argv=['x','--start','x','--name','x']
src=open(H/'fea-size-v1.py').read().split("V = json.loads(Path(args.start)")[0]
ns={'__file__':str(H/'fea-size-v1.py')}
exec(compile(src,'fea-size-v1','exec'),ns)
R=json.load(open(OUT/sys.argv[0] if False else OUT/Path(sys.stdin.readline().strip()).name))
ratios,D=ns['evaluate'](R)
best={}
for m,(r,c) in ratios.items():
    g=ns['group'](m)
    if g not in best or r>best[g][0]: best[g]=(r,m,c,D.get(m,0))
for m,dd in D.items():
    g=ns['group'](m)
    if g and (g not in best or dd>best[g][3]): 
        if g in best: best[g]=(best[g][0],best[g][1],best[g][2],dd)
for g,v in sorted(best.items(),key=lambda kv:-kv[1][0]): print('%-12s ratio %.2f %-6s %-28s D %.2f'%(g,v[0],v[1],v[2],v[3]))

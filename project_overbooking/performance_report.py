import pandas as pd


def get_total(filename, kind='db'):
    df = pd.read_csv(filename, header=None, sep=' ')
    v1 = (df[::2][1] * 1000).reset_index()[1]
    v2 = (df[1::2][1] * 1000).reset_index()[1]
    if kind == 'db':
        return v1
    elif kind == 'tree':
        return v2
    return v1 + v2


columns = ['10', '100', '1000']
d = []
for c in columns:
    d.append(get_total('po_perf_%s' % c))
df = pd.concat(d, axis=1)
df.columns = ['20', '200', '2000']
print df
ax = df.plot(
    kind='box')

ax.set_xlabel('number of elements in tree')
ax.set_ylabel('processing time, ms')
fig = ax.get_figure()
fig.savefig('performance_report.png')

import pandas as pd
import numpy as np
import os

def read_file(f):
    try:
        df = pd.read_csv(f, encoding='windows-1255', index_col=None)
    except:
        try:
            df = pd.read_csv(f, encoding='utf-8', index_col=None)
        except:
            print("Can't read %s" % f)
            df = None
    return df

path = r"C:\sigal\sigal_personal\elections26"
df_locs = read_file(os.path.join(path, "El25_kalfi_locs.csv"))
df_locs.columns=['csign', 'cname', 'msign', 'mname', 'ksign', 'gsign', 'address', 'location', 'acc', 'acc2', 'num_voters']
df_locs['num_voters'] = [int(x.replace(",","")) for x in df_locs.num_voters]
df_votes = {}
for e in [22,23,24,25]:
    df_votes[e] = read_file(os.path.join(path, "El%d_by_kalfi.csv" % e))
    df_votes[e].columns = ['csign', 'iron', 'mname', 'msign', 'ksign_p', 'cons',
                         'judge', 'tot_voters', 'num_voted', 'num_bad', 'num_good'] +  list(df_votes[e].columns[11:])
    df_votes[e]['ksign'] = df_votes[e].ksign_p.astype(int)

party = {}
for e in [22, 23, 24, 25]:
    v = df_votes[e][df_votes[e].columns[11:-1]].sum()
    party[e] = v[v>(v.sum()/120)].index
    if e == 22:
        print(e, len(party[e]))
    else:
        print(e, len(party[e]), len(set(party[e-1]).difference(party[e])),
              len(set(party[e]).difference(party[e-1])))
    print(list(party[e]))

parties = {}
parties['arab'] = ['ודעם', 'עם', 'ום', 'ד']
parties['hared'] = ['שס',  'ג']
parties['coal'] = ['מחל', 'טב', 'כף', 'ט']
parties['opos'] = ['פה',  'ל', 'מרצ', 'אמת',  'כן']
parties['not'] = ['ב',  'ת']

info = {}
for e in [22, 23, 24, 25]:
    info[e] = df_votes[e][['mname', 'msign', 'ksign_p', 'tot_voters', 'num_voted', 'num_bad', 'num_good']]
    for p in parties.keys():
        info[e][p] = df_votes[e][list(set(df_votes[e].columns).intersection(parties[p]))].sum(axis=1)
    print(info[e][list(parties.keys())].sum()/info[e][list(parties.keys())].sum().sum())


muni_info = {}
muni_vote = {}
miss = {}
over = {}
cols = ['muni', 'num_sub_kalfi_by_loc', 'num_kalfi_by_loc', 'num_voters_by_loc', 'sub_kalfi_list_loc']
colsv = ['muni']
for e in [22, 23, 24, 25]:
    miss[e] = []
    over[e] = list(set(df_votes[e].msign).difference(df_locs.msign))
    cols += ['num_sub_kalfi_by_vote%d' % e, 'num_kalfi_by_vote%d' % e, 'num_voters_by_vote%d' % e,
             'sub_kalfi_list_vote%d' % e]
    colsv += ['tot_voters%d' % e, 'num_voted%d' % e, 'num_good%d' % e]
    for p in parties.keys():
        colsv += ['num_%s%d' % (p, e)]
for m, tmp_loc in df_locs.groupby('msign'):
    muni_info[m] = [tmp_loc.mname.iloc[0], len(tmp_loc), len(set(tmp_loc.ksign)), int(tmp_loc.num_voters.sum()),
                    list(tmp_loc.ksign)]
    muni_vote[m] = [tmp_loc.mname.iloc[0]]
    for e in [22, 23, 24, 25]:
        df_m = df_votes[e][df_votes[e].msign==m]
        if len(df_m) == 0:
            miss[e].append(m)
            muni_info[m] += [None] * 4
            muni_vote[m] += [None] * (3+len(parties))
        else:
            muni_info[m] += [len(df_m), len(set(df_m.ksign)), int(df_m.tot_voters.sum()), list(df_m.ksign_p)]
            muni_vote[m] += [int(df_m.tot_voters.sum()), int(df_m.num_voted.sum()), int(df_m.num_good.sum())]
            for p in parties.keys():
                muni_vote[m] += [int(df_m[list(set(df_m.columns).intersection(parties[p]))].sum(axis=1).sum())]

print("vote over miss")
for e in [22, 23, 24, 25]:
    if e == 22:
        print(e, len(over[e]), len(miss[e]))
    else:
        print(e, len(over[e]), len(set(over[e-1]).difference(over[e])), len(set(over[e]).difference(over[e-1])), len(miss[e]), len(set(miss[e-1]).difference(miss[e])), len(set(miss[e]).difference(miss[e-1])))

muni_info = pd.DataFrame(muni_info, index=cols).T
muni_vote = pd.DataFrame(muni_vote, index=colsv).T

tmp = [[], []]
for e in [22, 23, 24, 25]:
    tmp[0].append(muni_vote['num_good%d' % e]/muni_vote['tot_voters%d' % e])
    tmp[1].append(muni_vote['num_opos%d' % e]/muni_vote['num_good%d' % e])
tmp[0] = pd.DataFrame(tmp[0])
tmp[1] = pd.DataFrame(tmp[1])
muni_vote['avg_prop_vote'] = tmp[0].mean()
muni_vote['std_prop_vote'] = tmp[0].std()
muni_vote['avg_prop_op'] = tmp[1].mean()
muni_vote['std_prop_op'] = tmp[1].std()

cs = ['avg_prop_vote', 'std_prop_vote', 'avg_prop_op', 'std_prop_op']
for c in cs:
    print(c)
    print(muni_vote[['muni'] + cs].sort_values(c, ascending=False).head(10))


print()

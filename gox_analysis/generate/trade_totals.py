# script to summarize per month/year and country
#   bitcoins sold
#   bitcoins bought
#   total
#   unique users
import glob
import csv
import json
from os import path
from collections import defaultdict

invalid_trades = set(['1385814706424312']) # corrupted trade record
trades_files_path = '../files/mtgox/trades'
outfile = 'html/data/trade_data_per_country.json'
trades_files = [
'2011-04.csv',
'2011-05.csv',
'2011-06.csv',
'2011-07.csv',
'2011-08.csv',
'2011-09.csv',
'2011-10.csv',
'2011-11.csv',
'2011-12.csv',
'2012-01.csv',
'2012-02.csv',
'2012-03.csv',
'2012-04.csv',
'2012-05.csv',
'2012-06.csv',
'2012-07.csv',
'2012-08.csv',
'2012-09.csv',
'2012-10.csv',
'2012-11_mtgox_japan.csv',
'2012-12_mtgox_japan.csv',
'2013-01_mtgox_japan.csv',
'2013-02_mtgox_japan.csv',
'2013-03_mtgox_japan.csv',
'2013-04_mtgox_japan.csv', # missing User_Country data and only goes up to 16th!
'2013-05_mtgox_japan.csv',
'2013-06_mtgox_japan.csv',
'2013-07_mtgox_japan.csv',
'2013-08_mtgox_japan.csv',
'2013-09_mtgox_japan.csv',
'2013-10_mtgox_japan.csv',
'2013-11_mtgox_japan.csv'
# ignoring the *_coinlab.csv, as all the transactions are the same as in _mtgox_japan but drop
# some information
]

data = defaultdict(float)
users = defaultdict(set)
for filename in trades_files:
    with open(path.join(trades_files_path, filename), 'r') as f:
        rdr = iter(csv.reader(f))
        hdr = next(rdr)
        hdr = dict([(a,b) for (b,a) in enumerate(hdr)])

        if not 'User_Country' in hdr:
            print "File %s has no country information, skipping" % filename
            continue
        print filename
        for rec in rdr:
            trade_id = int(rec[hdr['Trade_Id']])
            if rec[hdr['Trade_Id']] in invalid_trades:
                continue # weird
            type_ = rec[hdr['Type']]
            user_id = rec[hdr['User_Id']]
            amount = rec[hdr['Bitcoins']]
            dedup_id = (trade_id, type_, user_id, amount)
            #if dedup_id in all_trades:
            #    print "Warning: duplicate trade ", dedup_id
            #    continue
            date = rec[hdr['Date']]
            grouping = '' # currently not used: date[0:4] is year
            try:
                country = rec[hdr['User_Country']]
            except Exception:
                country = ''
            data[grouping,country,type_] += float(amount)
            users[grouping,country].add(user_id)
            #all_trades.add(dedup_id)

# Compute bitcoin trade difference per country
with open(outfile, 'w') as f:
    keys = set([(grouping,country) for (grouping,country,type_) in data.keys()])
    keys = sorted(list(keys))
    dataout = {'buy':{}, 'sell':{}, 'total':{}, 'users':{}}
    for key in keys:
       total_buy = data[key+('buy',)]
       total_sell = data[key+('sell',)]
       dataout['buy'][key[1]] = total_buy
       dataout['sell'][key[1]] = total_sell
       dataout['total'][key[1]] = total_buy-total_sell
       dataout['users'][key[1]] = len(users[key])
   
    json.dump(dataout, f, sort_keys=True, indent=4, separators=(',', ': '))


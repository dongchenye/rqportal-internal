from pandas import read_csv
from pandas.util.testing import assert_frame_equal

import rqportal

rqportal.init('test.yaml')
runid = 2012
rqportal.trades(runid).to_csv("{}_trade.new".format(runid))
rqportal.portfolio(runid).to_csv("{}_portf.new".format(runid))
rqportal.positions(runid).to_csv("{}_position.new".format(runid))


trade_old = read_csv("{}_trade.old".format(runid))
portf_old = read_csv("{}_portf.old".format(runid))
posit_old = read_csv("{}_position.old".format(runid))

trade_new = read_csv("{}_trade.new".format(runid))
portf_new = read_csv("{}_portf.new".format(runid))
posit_new = read_csv("{}_position.new".format(runid))

trade_old = trade_old.reindex_axis(sorted(trade_old.columns), axis=1)
trade_new = trade_new.reindex_axis(sorted(trade_new.columns), axis=1)

print(trade_new.equals(trade_old))
print(portf_new.equals(portf_old))
print(posit_new.equals(posit_old))

assert_frame_equal(trade_old, trade_new)
assert_frame_equal(portf_old, portf_new)
assert_frame_equal(posit_old, posit_new)
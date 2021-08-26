#!/usr/bin/env python3
# Copyright (c) 2021 The Dogecoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""PayTxFee QA test.

# Tests wallet behavior of -paytxfee in relation to -mintxfee
"""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.mininode import CTransaction, NetworkThread
from test_framework.util import *
from decimal import Decimal
from io import BytesIO
from decimal import *
getcontext().prec = 10

class PayTxFeeTest(BitcoinTestFramework):

    def __init__(self):
        super().__init__()
        self.setup_clean_chain = True
        self.num_nodes = 4

    def setup_nodes(self, split=False):
        nodes = []

        # node 0 has txindex to track txs
        nodes.append(start_node(0, self.options.tmpdir,
            ["-debug", '-txindex']))

        # node 1 pays 0.1 DOGE on all txs due to implicit mintxfee = paytxfee
        nodes.append(start_node(1, self.options.tmpdir,
            ["-paytxfee=0.1", "-debug"]))

        # node 2 will always pay 1 DOGE on all txs because of explicit mintxfee
        nodes.append(start_node(2, self.options.tmpdir,
            ["-mintxfee=1", "-paytxfee=0.1", "-debug"]))

        # node 3 will always pay 0.1 DOGE on all txs despite explicit mintxfee of 0.01
        nodes.append(start_node(3, self.options.tmpdir,
            ["-mintxfee=0.01", "-paytxfee=0.1", "-debug"]))

        return nodes

    def run_test(self):

        #print("START")
        #print( self.nodes[0].getwalletinfo() )
        #print( self.nodes[1].getwalletinfo() )
        #print( self.nodes[2].getwalletinfo() )
        #print( self.nodes[3].getwalletinfo() )

        seed = 1000 # the amount to seed wallets with
        amount = 995 # the amount to send back
        targetAddress = self.nodes[0].getnewaddress()

        # mine some blocks and prepare some coins
        self.nodes[0].generate(61)
        #print("")
        #print("After mining 61 blocks: ")
        #print( self.nodes[0].getwalletinfo() )
        #print( self.nodes[1].getwalletinfo() )
        #print( self.nodes[2].getwalletinfo() )
        #print( self.nodes[3].getwalletinfo() )
        self.nodes[0].sendtoaddress(self.nodes[1].getnewaddress(), seed)
        self.nodes[0].sendtoaddress(self.nodes[2].getnewaddress(), seed)
        self.nodes[0].sendtoaddress(self.nodes[3].getnewaddress(), seed)
        print("--------------------------------------------------------------")
        self.nodes[0].generate(1)
        self.sync_all()
        #print()
        #print("After sending 1000 coins to the same wallet to each node.")
        #print( self.nodes[0].getwalletinfo() )
        #print( self.nodes[1].getwalletinfo() )
        #print( self.nodes[2].getwalletinfo() )
        #print( self.nodes[3].getwalletinfo() )

        # create transactions
        txid1 = self.nodes[1].sendtoaddress(targetAddress, amount)
        txid2 = self.nodes[2].sendtoaddress(targetAddress, amount)
        txid3 = self.nodes[3].sendtoaddress(targetAddress, amount)
        self.sync_all()

        print("--------------------------------------------------------------")
        #print()
        #print("After sending 995 coins to the same wallet from each node.")
        #print( self.nodes[0].getwalletinfo() )
        #print( self.nodes[1].getwalletinfo() )
        #print( self.nodes[2].getwalletinfo() )
        #print( self.nodes[3].getwalletinfo() )

        # make sure correct fees were paid
        tx1 = self.nodes[0].getrawtransaction(txid1, True)
        tx2 = self.nodes[0].getrawtransaction(txid2, True)
        tx3 = self.nodes[0].getrawtransaction(txid3, True)

        print( 'vout', tx1['vout'][0]['value'] )
        print( 'vout', tx1['vout'][1]['value'] )
        print(  "tx1: ",tx1['size'],"   ",   tx1['vsize'] )
        print(  "tx2: ",tx2['size'],"   ",   tx2['vsize'] )
        print(  "tx3: ",tx3['size'],"   ",   tx3['vsize'] )

        c1 = (Decimal(len(tx1['hex'])/2)*Decimal(self.nodes[1].getwalletinfo()['paytxfee']))/Decimal(1000) 
        c2 = (Decimal(len(tx2['hex'])/2)*Decimal(self.nodes[2].getwalletinfo()['paytxfee']))/Decimal(100) 
        c3 = (Decimal(len(tx3['hex'])/2)*Decimal(self.nodes[3].getwalletinfo()['paytxfee']))/Decimal(1000) 

        t1 = tx1['vout'][1]['value'] if (tx1['vout'][1]['value'] < tx1['vout'][0]['value']) else tx1['vout'][0]['value']
        t2 = tx2['vout'][1]['value'] if (tx2['vout'][1]['value'] < tx2['vout'][0]['value']) else tx2['vout'][0]['value']
        t3 = tx3['vout'][1]['value'] if (tx3['vout'][1]['value'] < tx3['vout'][0]['value']) else tx3['vout'][0]['value']

        r1 = tx1['vout'][1]['value'] if (tx1['vout'][1]['value'] > tx1['vout'][0]['value']) else tx1['vout'][0]['value']
        r2 = tx2['vout'][1]['value'] if (tx2['vout'][1]['value'] > tx2['vout'][0]['value']) else tx2['vout'][0]['value']
        r3 = tx3['vout'][1]['value'] if (tx3['vout'][1]['value'] > tx3['vout'][0]['value']) else tx3['vout'][0]['value']
        
        print( "size(bytes) = ", len(tx1['hex'])/2,"   txfee:", c1, "   change:", t1, "   txfee + change:", t1 + c1, "   change + sent:",  t1 + r1  )
        print( "size(bytes) = ", len(tx2['hex'])/2,"   txfee:", c2, "   change:", t2, "   txfee + change:", t2 + c2, "   change + sent:",  t2 + r2  )
        print( "size(bytes) = ", len(tx3['hex'])/2,"   txfee:", c3, "   change:", t3, "   txfee + change:", t3 + c3, "   change + sent:",  t3 + r3  ) 

        assert_equal(tx1['vout'][0]['value'] + tx1['vout'][1]['value'], Decimal("999.9774"))
        assert_equal(tx2['vout'][0]['value'] + tx2['vout'][1]['value'], Decimal("999.774"))
        assert_equal(tx3['vout'][0]['value'] + tx3['vout'][1]['value'], Decimal("999.9774"))

        # mine a block
        self.nodes[0].generate(1);
        self.sync_all()

        # make sure all fees were mined
        block = self.nodes[0].getblock(self.nodes[0].getbestblockhash())
        coinbaseTx = self.nodes[0].getrawtransaction(block['tx'][0], True)

        assert_equal(coinbaseTx['vout'][0]['value'], Decimal("500000.2712"))

if __name__ == '__main__':
    PayTxFeeTest().main()

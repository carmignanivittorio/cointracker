from btc_api_wrappers.api_objects import Wallet

transaction_test = {'hash': '27fd4463f3554007a5bde48cb3b2a6e6ce2a687608972ac59ce904bb9cb43191', 'ver': 1, 'vin_sz': 1,
                    'vout_sz': 2, 'size': 224, 'weight': 566, 'fee': 429, 'relayed_by': '0.0.0.0', 'lock_time': 0,
                    'tx_index': 5108565427052701, 'double_spend': False, 'time': 1635331567, 'block_index': 706922,
                    'block_height': 706922, 'inputs': [{'sequence': 4294967295,
                                                        'witness': '02483045022100864229b7abbd3607d4c8de2533e28ace2b7da63899cdbf527eb1ce91c8b2b07502201a99ab30c75990e896557c299172f80ff7a868fb67f7c9031f607ff6ab11aa6b012103929ab76687d25261aa0e83ebcfde70d003d904e563e4992f691c1972417e3d4c',
                                                        'script': '', 'index': 0,
                                                        'prev_out': {'tx_index': 3466012746773228, 'value': 666601,
                                                                     'n': 1, 'type': 0, 'spent': True,
                                                                     'script': '00147c1051b60b552885fdb0de1271d9fed57ac01157',
                                                                     'spending_outpoints': [
                                                                         {'tx_index': 5108565427052701, 'n': 0}],
                                                                     'addr': 'bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5'}}],
                    'out': [{'type': 0, 'spent': True, 'value': 19700,
                             'spending_outpoints': [{'tx_index': 5604180826809468, 'n': 56}], 'n': 0,
                             'tx_index': 5108565427052701, 'script': 'a91488820d029b4a8d99d171050369c8fef0559efc0487',
                             'addr': '3E8ociqZa9mZUSwGdSmAEMAoAxBK3FNDcd'}, {'type': 0, 'spent': True, 'value': 646472,
                                                                             'spending_outpoints': [
                                                                                 {'tx_index': 780077689461979, 'n': 0}],
                                                                             'n': 1, 'tx_index': 5108565427052701,
                                                                             'script': '00142e38544a6ad4780ddfaec5ce89167a82ba7cee74',
                                                                             'addr': 'bc1q9cu9gjn263uqmhawch8gj9n6s2a8emn59e23vv'}],
                    'result': -666601, 'balance': 0}


wallet_2 = Wallet(address='bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5', n_tx=2, total_sent=0, total_received=0,
                  final_balance=0)

wallet_246 = Wallet(address='3JptJ5i3d5iSAK3k9QrSZ5qWHdxgHK6nHs', n_tx=246, total_sent=0, total_received=0,
                    final_balance=0)

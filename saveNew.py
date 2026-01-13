import base64
import pxsol

pxsol.config.current.log = 0

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))


def save(user: pxsol.wallet.Wallet, data: bytearray) -> None:
    prog_pubkey = pxsol.core.PubKey.base58_decode('BCPbAHyTpLUrKf6ov5h3BPyVw1NGifqFQS4ajTndyWVE')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)[0]
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    rq.data = data
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)


def load(user: pxsol.wallet.Wallet) -> bytearray:
    prog_pubkey = pxsol.core.PubKey.base58_decode('BCPbAHyTpLUrKf6ov5h3BPyVw1NGifqFQS4ajTndyWVE')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)[0]
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    return base64.b64decode(info['data'][0])


if __name__ == '__main__':
    save(ada, b'The quick brown fox jumps over the lazy dog')
    print(load(ada).decode()) # The quick brown fox jumps over the lazy dog
    save(ada, '片云天共远, 永夜月同孤.'.encode())
    print(load(ada).decode()) # 片云天共远, 永夜月同孤.

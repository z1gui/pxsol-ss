import base64
import pxsol

pxsol.config.current.log = 0

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))


def load(user: pxsol.wallet.Wallet) -> bytearray:
    prog_pubkey = pxsol.core.PubKey.base58_decode('BCPbAHyTpLUrKf6ov5h3BPyVw1NGifqFQS4ajTndyWVE')

    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)[0]
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    return base64.b64decode(info['data'][0])


if __name__ == '__main__':
    print(load(ada).decode()) # The quick brown fox jumps over the lazy dog

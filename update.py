import pathlib
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
program_pubkey = pxsol.core.PubKey.base58_decode('BCPbAHyTpLUrKf6ov5h3BPyVw1NGifqFQS4ajTndyWVE')
program_data = pathlib.Path('target/deploy/pxsol_ss.so').read_bytes()
ada.program_update(program_pubkey, program_data)

import pathlib
import pxsol

# Enable log
pxsol.config.current.log = 0

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

program_data = pathlib.Path('target/deploy/pxsol_ss.so').read_bytes()
program_pubkey = ada.program_deploy(bytearray(program_data))
print(program_pubkey) # BCPbAHyTpLUrKf6ov5h3BPyVw1NGifqFQS4ajTndyWVE

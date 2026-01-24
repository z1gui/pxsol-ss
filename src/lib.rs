#![allow(unexpected_cfgs)]

use solana_program::sysvar::Sysvar;

solana_program::entrypoint!(process_instruction);

pub fn process_instruction(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    let accounts_iter = &mut accounts.iter();
    //用户账户，相当于钱包账户
    let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
    //PDA账户
    let account_data = solana_program::account_info::next_account_info(accounts_iter)?;
    //系统账户，没用到
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program system
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program sysvar rent
    //计算数据最小的租金
    let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(data.len());
    //缺少判断派生PDA账户是该用户账户创建的
    //let bump_seed = solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id).1;
    //通过用户账户和程序ID计算PDA地址和碰撞修正值
    let calculated_pda =
    solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id);
    //判断传入的PDA是否正确
    assert_eq!(account_data.key, &calculated_pda.0); // Ensure the PDA is correct.
    //获取碰撞修正值
    let bump_seed = calculated_pda.1;

    // Data account is not initialized. Create an account and write data into it.
    // 判断PDA账户是否已经初始化
    if **account_data.try_borrow_lamports().unwrap() == 0 {
        //lamports为 0 ，未初始化就创建并签名
        solana_program::program::invoke_signed(
            &solana_program::system_instruction::create_account(
                //创建使用的租金从用户账户来
                account_user.key,
                //创建账户地址
                account_data.key,
                //租金，通过计算数据最小的租金获取
                rent_exemption,
                //数据大小
                data.len() as u64,
                //PDA账户所属owner
                program_id,
            ),
            accounts,
            //签名，通过用户账户签名
            &[&[&account_user.key.to_bytes(), &[bump_seed]]],
        )?;
        //写入数据
        account_data.data.borrow_mut().copy_from_slice(data);
        return Ok(());
    }

    // Fund the data account to let it rent exemption.
    // 租金补足，从用户账户中转
    if rent_exemption > account_data.lamports() {
        solana_program::program::invoke(
            &solana_program::system_instruction::transfer(
                account_user.key,
                account_data.key,
                rent_exemption - account_data.lamports(),
            ),
            accounts,
        )?;
    }
    // Withdraw excess funds and return them to users. Since the funds in the pda account belong to the program, we do
    // not need to use instructions to transfer them here.
    // 租赁退款，退回用户，因为PDA账户属于程序，不需要使用指令来转移
    if rent_exemption < account_data.lamports() {
        **account_user.lamports.borrow_mut() = account_user.lamports() + account_data.lamports() - rent_exemption;
        **account_data.lamports.borrow_mut() = rent_exemption;
    }
    // Realloc space.
    account_data.realloc(data.len(), false)?;
    // Overwrite old data with new data.
    account_data.data.borrow_mut().copy_from_slice(data);

    Ok(())
}

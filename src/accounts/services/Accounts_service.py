from ..models.Accounts import AccountCreate, AccountUpdate, AccountView, AccountBase, AccountUpdatebalance
from ..db.AccountsRepository import AccountRepository
from ..core import extensions as ext

from schwifty import IBAN

from ..models.Empty import EmptyPatch403, EmptyPatch404


# Implement cache here

class AccountService:
    def __init__(self, repository: AccountRepository | None = None):
        self.repo = repository or AccountRepository(ext.db)
    
    async def create_new_account(self, data: AccountCreate) -> AccountView:
        data_dict = data.model_dump(by_alias=True)
        
        iban_es = IBAN.random(country_code='ES')
        data_dict['iban'] = str(iban_es)
        
        new_account = AccountBase(**data_dict)
        
        return await self.repo.insert_account(new_account)
    
    async def get_account_by_iban(self, iban: str) -> AccountView | None:
        return await self.repo.find_account_by_iban(iban=iban)
    
    async def account_update(self, iban:str, data: AccountUpdate) -> AccountView:
        return await self.repo.update_account(iban, data)
    
    async def account_update_balance(self, iban:str, data: AccountUpdatebalance) -> AccountView | EmptyPatch404 | EmptyPatch403:
        acc = await self.repo.find_account_by_iban(iban)
        if not acc:
            return EmptyPatch404()
        
        if acc.balance + data.balance > 0 :
            data.balance = acc.balance + data.balance
            return await self.repo.update_account_balance(iban, data)
        else:
            return EmptyPatch403()
        
        
    
    async def delete_account(self, iban: str):
        return await self.repo.delete_account_by_iban(iban)
    
    async def block_account(self, iban: str):
        return await self.repo.block_account_by_iban(iban)
    
    async def unblock_account(self, iban: str):
        return await self.repo.unblock_account_by_iban(iban)
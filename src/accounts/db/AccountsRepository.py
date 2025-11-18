from logging import getLogger

from ..models.Accounts import AccountCreate, AccountUpdate, AccountView, AccountUpdatebalance, AccountBase


logger = getLogger()

class AccountRepository:
    
    def __init__(self, db):
        self.collection = db["accounts"]     # Collection used here
    
    async def insert_account(self, data: AccountBase) -> AccountView:
        account_doc = data.model_dump(by_alias=True)
        
        result = await self.collection.insert_one(account_doc)
        created_doc = await self.collection.find_one({"_id": result.inserted_id})
        
        return AccountView.model_validate(created_doc)
    
    async def find_account_by_iban(self, iban: str) -> AccountView | None:
        doc = await self.collection.find_one({"iban": iban})
        
        return AccountView.model_validate(doc) if doc else None
    
    async def delete_account_by_iban(self, iban: str) -> bool:
        result = await self.collection.delete_one({"iban": iban})
        return result.deleted_count > 0
    
    async def update_account_balance(self, iban: str, data: AccountUpdatebalance) -> AccountView | None:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        
        if not update_data:
            modified = await self.find_account_by_iban(iban)
            return AccountView.model_validate(modified)
        
        await self.collection.update_one(
            {"iban": iban},
            {"$set": update_data}
            )
        
        modified = await self.find_account_by_iban(iban)
        return AccountView.model_validate(modified) if modified else None
    
    async def update_account(self, iban: str, data: AccountUpdate) -> AccountView | None:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        
        if not update_data:
            modified = await self.find_account_by_iban(iban)
            return AccountView.model_validate(modified)
        
        await self.collection.update_one(
            {"iban": iban},
            {"$set": update_data}
            )
        
        modified = await self.find_account_by_iban(iban)
        return AccountView.model_validate(modified) if modified else None
    
    async def block_account_by_iban(self, iban: str) -> AccountView | None:
        await self.collection.update_one(
            {"iban": iban},
            {"$set": {"isBlocked": True}}
            )
        
        modified = await self.find_account_by_iban(iban)
        return AccountView.model_validate(modified) if modified else None
    
    async def unblock_account_by_iban(self, iban: str) -> AccountView | None:
        await self.collection.update_one(
            {"iban": iban},
            {"$set": {"isBlocked": False}}
            )
        
        modified = await self.find_account_by_iban(iban)
        return AccountView.model_validate(modified) if modified else None
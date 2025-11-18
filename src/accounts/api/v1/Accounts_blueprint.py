from quart import Blueprint, request, abort
from quart_schema import validate_request, validate_response, tag, document_request, document_response

from ...models.Accounts import AccountCreate, AccountUpdate, AccountView, AccountUpdatebalance, AccountBase
from ...models.Empty import EmptyGet404, EmptyPatch400, EmptyPatch403, EmptyPatch404

from ...services.Accounts_service import AccountService

from logging import getLogger
from ...core.config import settings

logger = getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)

bp = Blueprint("accounts_v1", __name__, url_prefix="/v1/accounts")


@bp.post("/")
@validate_request(AccountCreate)
@validate_response(AccountView, 201)
@tag(["v1"])
async def create_account(data: AccountCreate):
    service = AccountService()
    return await service.create_new_account(data), 201

@bp.get("/<string:iban>")
@validate_response(AccountView, 200)
@document_response(EmptyGet404, 404)
@tag(["v1"])
async def view_account(iban: str):
    service = AccountService()
    res = await service.get_account_by_iban(iban)
    return res if res else abort(404, description="Account not found")

@bp.patch("/<string:iban>")
@document_request(AccountUpdate)    #Document request to allow patch individual fields
@validate_response(AccountView)
@document_response(EmptyPatch400, 400)
@tag(["v1"])
async def update_account(iban: str):
    service = AccountService()
    
    # Validate JSON here
    raw_data = await request.get_json()
    if raw_data is None:
        return abort(400, description="Bad Request")
    data = AccountUpdate(**raw_data)
    
    res = await service.account_update(iban, data)
    return res if res else abort(404, description="Account not found")

@bp.patch("/operation/<string:iban>")
@document_request(AccountUpdatebalance)
@validate_response(AccountView)
@document_response(EmptyPatch400, 400)
@document_response(EmptyPatch403, 403)
@document_response(EmptyPatch404, 404)
@tag(["v1"])
async def update_account_balance(iban: str):
    service = AccountService()
    
    # Validate JSON here
    raw_data = await request.get_json()
    if raw_data is None:
        return abort(400, description="Bad Request")
    data = AccountUpdatebalance(**raw_data)
    
    res = await service.account_update_balance(iban, data)
    if isinstance(res, EmptyPatch403):
        abort(403, description="Forbidden Operation - Not sufficient funds")
    elif isinstance(res, EmptyPatch404):
        abort(404, description="Account not found")
    return res

@bp.delete("/<string:iban>")
@tag(["v1"])
async def delete_account(iban: str):
    service = AccountService()
    await service.delete_account(iban)
    return "",204

@bp.patch("/<string:iban>/block")
@validate_response(AccountView)
@tag(["v1"])
async def block_account(iban: str):
    service = AccountService()
    res = await service.block_account(iban)
    return "", 204 if res else abort(404, description="Account not found")

@bp.patch("/<string:iban>/unblock")
@validate_response(AccountView)
@tag(["v1"])
async def unblock_account(iban: str):
    service = AccountService()
    res = await service.unblock_account(iban)
    return "", 204 if res else abort(404, description="Account not found")
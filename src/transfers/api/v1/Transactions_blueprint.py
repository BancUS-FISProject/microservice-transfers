from quart import Blueprint, request, abort, jsonify
from quart_schema import validate_request, validate_response, tag

from ...models.Transactions import TransactionCreate, TransactionView
from ...services.Transfers_service import TransferService

from logging import getLogger
from ...core.config import settings

logger = getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)

bp = Blueprint("transfers_v1", __name__, url_prefix="/v1/transactions")


@bp.post("/")
@validate_request(TransactionCreate)
async def create_transaction(data: TransactionCreate):
    service = TransferService()
    try:
        res = await service.create_transaction(data)
    except ValueError as e:
        abort(400, description=str(e))

    if res.get("status") == "completed":
        return res["transaction"], 202
    else:
        return jsonify(res), 400

@bp.get("/<string:id>")
async def get_transaction(id: str):
    service = TransferService()
    res = await service.get_transaction(id)
    if not res:
        abort(404, description="Transaction not found")
    return res, 200

@bp.get("/user/<string:id>")
async def get_transactions_by_user(id: str):
    service = TransferService()
    res = await service.get_transactions_by_user(id)
    if not res:
        abort(404, description="No transactions found for user")
    return res, 200

@bp.get("/user/<string:id>/sent")
async def get_transactions_sent(id: str):
    service = TransferService()
    res = await service.get_transactions_sent_by_user(id)
    if not res:
        abort(404, description="No sent transactions found for user")
    return res, 200

@bp.get("/user/<string:id>/received")
async def get_transactions_received(id: str):
    service = TransferService()
    res = await service.get_transactions_received_by_user(id)
    if not res:
        abort(404, description="No received transactions found for user")
    return res, 200

@bp.patch("/<string:id>")
async def revert_transaction(id: str):
    service = TransferService()
    res = await service.revert_transaction(id)
    if res is None:
        abort(404, description="Transaction not found")
    if res.get("status") == "reverted":
        return res["transaction"], 200
    else:
        return jsonify(res), 400

@bp.delete("/<string:id>")
async def delete_transaction(id: str):
    service = TransferService()
    res = await service.delete_transaction(id)
    if res is None:
        abort(404, description="Transaction not found")

    if res.get("status") == "deleted":
        return res["transaction"], 200
    else:
        return jsonify(res), 400


@bp.put("/<string:id>/status")
async def put_status(id: str):
    payload = await request.get_json(silent=True) or {}
    new_status = payload.get("status")
    if not new_status:
        abort(400, description="Missing 'status' in request body")

    service = TransferService()
    res = await service.update_status(id, new_status)
    if res is None:
        abort(404, description="Transaction not found")

    if res.get("status") == "updated":
        return res["transaction"], 200
    else:
        return jsonify(res), 400

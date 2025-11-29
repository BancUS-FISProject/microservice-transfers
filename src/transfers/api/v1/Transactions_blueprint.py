from quart import Blueprint, request, abort, jsonify, current_app
from quart_schema import validate_request, validate_response, tag
from typing import List

from ...models.Transactions import TransactionCreate, TransactionView, ErrorResponse, StatusUpdateRequest
from ...services.Transfers_service import TransferService

from logging import getLogger
from ...core.config import settings

logger = getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)

bp = Blueprint("transfers_v1", __name__, url_prefix="/v1/transactions")


@bp.post("/")
@tag(["transactions"])
@validate_request(TransactionCreate)
@validate_response(TransactionView, 202)
@validate_response(ErrorResponse, 400)
@validate_response(ErrorResponse, 503)
async def create_transaction(data: TransactionCreate):
    """
    Crea una nueva transacción entre dos cuentas.
    
    Realiza una transferencia de fondos desde la cuenta del remitente a la cuenta del receptor.
    Valida que el remitente tenga suficientes fondos antes de completar la transacción.
    """
    service = TransferService(redis_client=getattr(current_app, "redis_client", None))
    try:
        res = await service.create_transaction(data)
    except ValueError as e:
        abort(400, description=str(e))

    if res.get("status") == "completed":
        return res["transaction"], 202
    elif res.get("reason") == "service_unavailable":
        return jsonify(res), 503
    else:
        return jsonify(res), 400

@bp.get("/<string:id>")
@tag(["transactions"])
@validate_response(TransactionView, 200)
@validate_response(ErrorResponse, 404)
async def get_transaction(id: str):
    """
    Obtiene los detalles de una transacción específica.
    
    Retorna la información completa de una transacción usando su ID único.
    """
    service = TransferService(redis_client=getattr(current_app, "redis_client", None))
    res = await service.get_transaction(id)
    if not res:
        abort(404, description="Transaction not found")
    return res, 200

@bp.get("/user/<string:id>")
@tag(["transactions"])
@validate_response(List[TransactionView], 200)
@validate_response(ErrorResponse, 404)
async def get_transactions_by_user(id: str):
    """
    Obtiene todas las transacciones de un usuario.
    
    Retorna todas las transacciones donde el usuario aparece como remitente o receptor.
    """
    service = TransferService(redis_client=getattr(current_app, "redis_client", None))
    res = await service.get_transactions_by_user(id)
    if not res:
        abort(404, description="No transactions found for user")
    return res, 200

@bp.get("/user/<string:id>/sent")
@tag(["transactions"])
@validate_response(List[TransactionView], 200)
@validate_response(ErrorResponse, 404)
async def get_transactions_sent(id: str):
    """
    Obtiene las transacciones enviadas por un usuario.
    
    Retorna todas las transacciones donde el usuario es el remitente.
    """
    service = TransferService(redis_client=getattr(current_app, "redis_client", None))
    res = await service.get_transactions_sent_by_user(id)
    if not res:
        abort(404, description="No sent transactions found for user")
    return res, 200

@bp.get("/user/<string:id>/received")
@tag(["transactions"])
@validate_response(List[TransactionView], 200)
@validate_response(ErrorResponse, 404)
async def get_transactions_received(id: str):
    """
    Obtiene las transacciones recibidas por un usuario.
    
    Retorna todas las transacciones donde el usuario es el receptor.
    """
    service = TransferService(redis_client=getattr(current_app, "redis_client", None))
    res = await service.get_transactions_received_by_user(id)
    if not res:
        abort(404, description="No received transactions found for user")
    return res, 200

@bp.patch("/<string:id>")
@tag(["transactions"])
@validate_response(TransactionView, 200)
@validate_response(ErrorResponse, 400)
@validate_response(ErrorResponse, 404)
@validate_response(ErrorResponse, 503)
async def revert_transaction(id: str):
    """
    Revierte una transacción completada.
    
    Devuelve los fondos a la cuenta del remitente y actualiza el estado de la transacción a 'reverted'.
    Solo se pueden revertir transacciones que estén en estado 'completed'.
    """
    service = TransferService(redis_client=getattr(current_app, "redis_client", None))
    res = await service.revert_transaction(id)
    if res is None:
        abort(404, description="Transaction not found")
    if res.get("status") == "reverted":
        return res["transaction"], 200
    elif res.get("reason") == "service_unavailable":
        return jsonify(res), 503
    else:
        return jsonify(res), 400

@bp.delete("/<string:id>")
@tag(["transactions"])
@validate_response(TransactionView, 200)
@validate_response(ErrorResponse, 400)
@validate_response(ErrorResponse, 404)
async def delete_transaction(id: str):
    """
    Elimina una transacción del sistema.
    
    Marca una transacción como eliminada. Solo se pueden eliminar transacciones en estado 'pending' o 'failed'.
    """
    service = TransferService(redis_client=getattr(current_app, "redis_client", None))
    res = await service.delete_transaction(id)
    if res is None:
        abort(404, description="Transaction not found")

    if res.get("status") == "deleted":
        return res["transaction"], 200
    else:
        return jsonify(res), 400


@bp.put("/<string:id>/status")
@tag(["transactions"])
@validate_request(StatusUpdateRequest)
@validate_response(TransactionView, 200)
@validate_response(ErrorResponse, 400)
@validate_response(ErrorResponse, 404)
async def put_status(id: str, data: StatusUpdateRequest):
    """
    Actualiza el estado de una transacción.
    
    Permite cambiar manualmente el estado de una transacción.
    Estados válidos: pending, completed, failed, reverted.
    """
    new_status = data.status

    service = TransferService(redis_client=getattr(current_app, "redis_client", None))
    res = await service.update_status(id, new_status)
    if res is None:
        abort(404, description="Transaction not found")

    if res.get("status") == "updated":
        return res["transaction"], 200
    else:
        return jsonify(res), 400

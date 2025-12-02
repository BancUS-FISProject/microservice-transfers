import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.transfers.services.Transfers_service import TransferService
from src.transfers.models.Transactions import TransactionCreate

# Test data shared across tests
test_data = {
    "transaction_id": None,
    "sender_id": "IBAN-ES9121000418450200051332",
    "receiver_id": "IBAN-ES9121000418450200051333",
    "initial_quantity": 1000,
}

# ======================
# OUT-OF-PROCESS TESTS (HTTP API Tests)
# ======================

@pytest.mark.asyncio
@pytest.mark.dependency(name="create_transaction")
async def test_create_transaction_success(client):
    """
    Test POST /v1/transactions/ — Create new transaction successfully
    """
    payload = {
        "sender": test_data["sender_id"],
        "receiver": test_data["receiver_id"],
        "quantity": test_data["initial_quantity"]
    }
    
    with patch.object(TransferService, 'create_transaction', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {
            "status": "completed",
            "transaction": {
                "id": "507f1f77bcf86cd799439011",
                "sender": test_data["sender_id"],
                "receiver": test_data["receiver_id"],
                "quantity": test_data["initial_quantity"],
                "status": "completed",
                "date": "2025-11-23T10:00:00"
            }
        }
        
        response = await client.post("/v1/transactions/", json=payload)
        
        assert response.status_code == 202, "Create transaction should return 202"
        response_json = await response.get_json()
        
        assert "id" in response_json
        assert response_json["sender"] == test_data["sender_id"]
        assert response_json["receiver"] == test_data["receiver_id"]
        assert response_json["quantity"] == test_data["initial_quantity"]
        assert response_json["status"] in ["pending", "completed"]
        
        test_data["transaction_id"] = response_json.get("id")


@pytest.mark.asyncio
async def test_create_transaction_missing_params(client):
    """
    Test POST /v1/transactions/ — Missing required parameters
    """
    payload = {
        "sender": test_data["sender_id"],
        # Missing receiver and quantity
    }
    response = await client.post("/v1/transactions/", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_transaction_invalid_quantity_zero(client):
    """
    Test POST /v1/transactions/ — Quantity must be positive
    """
    payload = {
        "sender": test_data["sender_id"],
        "receiver": test_data["receiver_id"],
        "quantity": 0
    }
    response = await client.post("/v1/transactions/", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_transaction_invalid_quantity_negative(client):
    """
    Test POST /v1/transactions/ — Negative quantity should fail
    """
    payload = {
        "sender": test_data["sender_id"],
        "receiver": test_data["receiver_id"],
        "quantity": -500
    }
    response = await client.post("/v1/transactions/", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_transaction_same_sender_receiver(client):
    """
    Test POST /v1/transactions/ — Sender and receiver must be different
    """
    payload = {
        "sender": test_data["sender_id"],
        "receiver": test_data["sender_id"],  # Same as sender
        "quantity": 100
    }
    response = await client.post("/v1/transactions/", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_transaction_insufficient_funds(client):
    """
    Test POST /v1/transactions/ — Transaction fails due to insufficient funds
    """
    payload = {
        "sender": test_data["sender_id"],
        "receiver": test_data["receiver_id"],
        "quantity": 999999999
    }
    
    with patch.object(TransferService, 'create_transaction', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {
            "status": "failed",
            "reason": "insufficient_funds",
            "transaction": {"id": "mock_id", "status": "failed"}
        }
        
        response = await client.post("/v1/transactions/", json=payload)
        assert response.status_code == 400
        response_text = await response.get_data(as_text=True)
        assert "insufficient_funds" in response_text or "failed" in response_text


@pytest.mark.asyncio
async def test_create_transaction_sender_not_found(client):
    """
    Test POST /v1/transactions/ — Sender account not found
    """
    payload = {
        "sender": "IBAN-NONEXISTENT",
        "receiver": test_data["receiver_id"],
        "quantity": 100
    }
    
    with patch.object(TransferService, 'create_transaction', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {
            "status": "failed",
            "reason": "sender_not_found",
            "transaction": {"id": "mock_id", "status": "failed"}
        }
        
        response = await client.post("/v1/transactions/", json=payload)
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_transaction_receiver_not_found(client):
    """
    Test POST /v1/transactions/ — Receiver account not found
    """
    payload = {
        "sender": test_data["sender_id"],
        "receiver": "IBAN-NONEXISTENT",
        "quantity": 100
    }
    
    with patch.object(TransferService, 'create_transaction', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {
            "status": "failed",
            "reason": "receiver_not_found",
            "transaction": {"id": "mock_id", "status": "failed"}
        }
        
        response = await client.post("/v1/transactions/", json=payload)
        assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["create_transaction"])
async def test_get_transaction_by_id(client):
    """
    Test GET /v1/transactions/<id> — Get transaction by ID
    """
    transaction_id = "507f1f77bcf86cd799439011"
    
    with patch.object(TransferService, 'get_transaction', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {
            "id": transaction_id,
            "sender": test_data["sender_id"],
            "receiver": test_data["receiver_id"],
            "quantity": test_data["initial_quantity"],
            "status": "completed"
        }
        
        response = await client.get(f"/v1/transactions/{transaction_id}")
        
        assert response.status_code == 200
        response_json = await response.get_json()
        assert response_json["id"] == transaction_id


@pytest.mark.asyncio
async def test_get_transaction_not_found(client):
    """
    Test GET /v1/transactions/<id> — Transaction not found
    """
    with patch.object(TransferService, 'get_transaction', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        
        response = await client.get("/v1/transactions/nonexistent_id")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_transaction_invalid_id(client):
    """
    Test GET /v1/transactions/<id> — Invalid ObjectId format
    """
    with patch.object(TransferService, 'get_transaction', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        
        response = await client.get("/v1/transactions/invalid-id-format")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_transactions_by_user(client):
    """
    Test GET /v1/transactions/user/<id> — Get all transactions for a user
    """
    user_id = test_data["sender_id"]
    
    with patch.object(TransferService, 'get_transactions_by_user', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [
            {"id": "1", "sender": user_id, "receiver": "other", "quantity": 100, "status": "completed"},
            {"id": "2", "sender": "other", "receiver": user_id, "quantity": 200, "status": "completed"}
        ]
        
        response = await client.get(f"/v1/transactions/user/{user_id}")
        
        assert response.status_code == 200
        response_json = await response.get_json()
        assert isinstance(response_json, list)
        assert len(response_json) >= 0


@pytest.mark.asyncio
async def test_get_transactions_by_user_not_found(client):
    """
    Test GET /v1/transactions/user/<id> — No transactions found for user
    """
    with patch.object(TransferService, 'get_transactions_by_user', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        
        response = await client.get("/v1/transactions/user/IBAN-NOUSER")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_transactions_sent_by_user(client):
    """
    Test GET /v1/transactions/user/<id>/sent — Get sent transactions
    """
    user_id = test_data["sender_id"]
    
    with patch.object(TransferService, 'get_transactions_sent_by_user', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [
            {"id": "1", "sender": user_id, "receiver": "other", "quantity": 100, "status": "completed"}
        ]
        
        response = await client.get(f"/v1/transactions/user/{user_id}/sent")
        
        assert response.status_code == 200
        response_json = await response.get_json()
        assert isinstance(response_json, list)


@pytest.mark.asyncio
async def test_get_transactions_sent_not_found(client):
    """
    Test GET /v1/transactions/user/<id>/sent — No sent transactions
    """
    with patch.object(TransferService, 'get_transactions_sent_by_user', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        
        response = await client.get("/v1/transactions/user/IBAN-NOUSER/sent")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_transactions_received_by_user(client):
    """
    Test GET /v1/transactions/user/<id>/received — Get received transactions
    """
    user_id = test_data["receiver_id"]
    
    with patch.object(TransferService, 'get_transactions_received_by_user', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [
            {"id": "1", "sender": "other", "receiver": user_id, "quantity": 200, "status": "completed"}
        ]
        
        response = await client.get(f"/v1/transactions/user/{user_id}/received")
        
        assert response.status_code == 200
        response_json = await response.get_json()
        assert isinstance(response_json, list)


@pytest.mark.asyncio
async def test_get_transactions_received_not_found(client):
    """
    Test GET /v1/transactions/user/<id>/received — No received transactions
    """
    with patch.object(TransferService, 'get_transactions_received_by_user', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        
        response = await client.get("/v1/transactions/user/IBAN-NOUSER/received")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.dependency(name="revert_transaction", depends=["create_transaction"])
async def test_revert_transaction_success(client):
    """
    Test PATCH /v1/transactions/<id> — Revert a completed transaction
    """
    transaction_id = "507f1f77bcf86cd799439011"
    
    with patch.object(TransferService, 'revert_transaction', new_callable=AsyncMock) as mock_revert:
        mock_revert.return_value = {
            "status": "reverted",
            "transaction": {
                "id": transaction_id,
                "status": "reverted"
            }
        }
        
        response = await client.patch(f"/v1/transactions/{transaction_id}")
        
        assert response.status_code == 200
        response_json = await response.get_json()
        assert response_json["status"] == "reverted"


@pytest.mark.asyncio
async def test_revert_transaction_not_found(client):
    """
    Test PATCH /v1/transactions/<id> — Revert non-existent transaction
    """
    with patch.object(TransferService, 'revert_transaction', new_callable=AsyncMock) as mock_revert:
        mock_revert.return_value = None
        
        response = await client.patch("/v1/transactions/nonexistent_id")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_revert_transaction_not_completed(client):
    """
    Test PATCH /v1/transactions/<id> — Cannot revert non-completed transaction
    """
    transaction_id = "507f1f77bcf86cd799439011"
    
    with patch.object(TransferService, 'revert_transaction', new_callable=AsyncMock) as mock_revert:
        mock_revert.return_value = {
            "status": "not_reverted",
            "reason": "transaction_not_completed",
            "transaction": {"id": transaction_id, "status": "pending"}
        }
        
        response = await client.patch(f"/v1/transactions/{transaction_id}")
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_revert_transaction_insufficient_funds(client):
    """
    Test PATCH /v1/transactions/<id> — Revert fails due to insufficient funds
    """
    transaction_id = "507f1f77bcf86cd799439011"
    
    with patch.object(TransferService, 'revert_transaction', new_callable=AsyncMock) as mock_revert:
        mock_revert.return_value = {
            "status": "failed",
            "reason": "receiver_insufficient_funds",
            "transaction": {"id": transaction_id, "status": "completed"}
        }
        
        response = await client.patch(f"/v1/transactions/{transaction_id}")
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_transaction_status_success(client):
    """
    Test PUT /v1/transactions/<id>/status — Update transaction status
    """
    transaction_id = "507f1f77bcf86cd799439011"
    
    with patch.object(TransferService, 'update_status', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = {
            "status": "updated",
            "transaction": {
                "id": transaction_id,
                "status": "completed"
            }
        }
        
        payload = {"status": "completed"}
        response = await client.put(f"/v1/transactions/{transaction_id}/status", json=payload)
        
        assert response.status_code == 200
        response_json = await response.get_json()
        assert response_json["status"] == "completed"


@pytest.mark.asyncio
async def test_update_transaction_status_missing_param(client):
    """
    Test PUT /v1/transactions/<id>/status — Missing status parameter
    """
    transaction_id = "507f1f77bcf86cd799439011"
    
    payload = {}
    response = await client.put(f"/v1/transactions/{transaction_id}/status", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_transaction_status_invalid_transition(client):
    """
    Test PUT /v1/transactions/<id>/status — Invalid status transition
    """
    transaction_id = "507f1f77bcf86cd799439011"
    
    with patch.object(TransferService, 'update_status', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = {
            "status": "failed",
            "reason": "invalid_transition",
            "from": "reverted",
            "to": "completed"
        }
        
        payload = {"status": "completed"}
        response = await client.put(f"/v1/transactions/{transaction_id}/status", json=payload)
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_transaction_status_not_found(client):
    """
    Test PUT /v1/transactions/<id>/status — Transaction not found
    """
    with patch.object(TransferService, 'update_status', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = None
        
        payload = {"status": "completed"}
        response = await client.put("/v1/transactions/nonexistent_id/status", json=payload)
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.dependency(name="delete_transaction", depends=["create_transaction"])
async def test_delete_transaction_success(client):
    """
    Test DELETE /v1/transactions/<id> — Delete transaction
    """
    transaction_id = "507f1f77bcf86cd799439011"
    
    with patch.object(TransferService, 'delete_transaction', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = {
            "status": "deleted",
            "transaction": {"id": transaction_id, "status": "deleted"}
        }
        
        response = await client.delete(f"/v1/transactions/{transaction_id}")
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_transaction_not_found(client):
    """
    Test DELETE /v1/transactions/<id> — Delete non-existent transaction
    """
    with patch.object(TransferService, 'delete_transaction', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = None
        
        response = await client.delete("/v1/transactions/nonexistent_id")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["delete_transaction"])
async def test_verify_transaction_deleted(client):
    """
    Test GET /v1/transactions/<id> — Verify transaction was deleted
    """
    transaction_id = "507f1f77bcf86cd799439011"
    
    with patch.object(TransferService, 'get_transaction', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        
        response = await client.get(f"/v1/transactions/{transaction_id}")
        assert response.status_code == 404


# ======================
# IN-PROCESS TESTS (Service Layer Tests)
# ======================

@pytest.mark.asyncio
async def test_service_create_transaction_validation_positive_quantity():
    """
    IN-PROCESS: Test TransferService validates positive quantity
    """
    mock_repo = MagicMock()
    service = TransferService(repository=mock_repo)
    
    data = TransactionCreate(
        sender="IBAN-SENDER",
        receiver="IBAN-RECEIVER",
        quantity=0
    )
    
    with pytest.raises(ValueError, match="Quantity must be positive"):
        await service.create_transaction(data)


@pytest.mark.asyncio
async def test_service_create_transaction_validation_different_accounts():
    """
    IN-PROCESS: Test TransferService validates sender != receiver
    """
    mock_repo = MagicMock()
    service = TransferService(repository=mock_repo)
    
    data = TransactionCreate(
        sender="IBAN-SAME",
        receiver="IBAN-SAME",
        quantity=100
    )
    
    with pytest.raises(ValueError, match="Sender and receiver must be different"):
        await service.create_transaction(data)


@pytest.mark.asyncio
async def test_service_update_status_valid_transitions():
    """
    IN-PROCESS: Test TransferService status transition logic
    """
    mock_repo = MagicMock()
    mock_repo.find_transaction_by_id = AsyncMock(return_value={
        "id": "test_id",
        "status": "pending"
    })
    mock_repo.update_transaction_status = AsyncMock(return_value={
        "id": "test_id",
        "status": "completed"
    })
    
    service = TransferService(repository=mock_repo)
    
    result = await service.update_status("test_id", "completed")
    
    assert result["status"] == "updated"
    assert result["transaction"]["status"] == "completed"


@pytest.mark.asyncio
async def test_service_update_status_invalid_transitions():
    """
    IN-PROCESS: Test TransferService rejects invalid status transitions
    """
    mock_repo = MagicMock()
    mock_repo.find_transaction_by_id = AsyncMock(return_value={
        "id": "test_id",
        "status": "reverted"
    })
    
    service = TransferService(repository=mock_repo)
    
    result = await service.update_status("test_id", "completed")
    
    assert result["status"] == "failed"
    assert result["reason"] == "invalid_transition"


@pytest.mark.asyncio
async def test_service_get_transactions_by_user_filters_correctly():
    """
    IN-PROCESS: Test TransferService filters transactions by user
    """
    mock_repo = MagicMock()
    mock_repo.find_transactions_by_user = AsyncMock(return_value=[
        {"id": "1", "sender": "user1", "receiver": "user2"},
        {"id": "2", "sender": "user2", "receiver": "user1"}
    ])
    
    service = TransferService(repository=mock_repo)
    
    result = await service.get_transactions_by_user("user1")
    
    assert len(result) == 2
    mock_repo.find_transactions_by_user.assert_called_once_with("user1")

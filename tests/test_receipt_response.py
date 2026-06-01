from handlers.photos import build_receipt_response


def test_build_receipt_response_with_items():
    entry = {
        "name": "Biedronka receipt",
        "amount": 25.50,
        "category": "groceries",
        "items": [
            {"name": "Milk", "amount": 4.99},
            {"name": "Bread", "amount": 3.50},
        ],
    }

    result = build_receipt_response(entry, "PLN", "en")

    assert "Biedronka receipt" in result
    assert "25.50 PLN" in result
    assert "Milk" in result
    assert "4.99 PLN" in result
    assert "Bread" in result
    assert "3.50 PLN" in result


def test_build_receipt_response_without_items():
    entry = {
        "name": "Lidl receipt",
        "amount": 10.00,
        "category": "groceries",
        "items": [],
    }

    result = build_receipt_response(entry, "PLN", "en")

    assert "Lidl receipt" in result
    assert "10.00 PLN" in result
    assert "🧾 Items:" not in result
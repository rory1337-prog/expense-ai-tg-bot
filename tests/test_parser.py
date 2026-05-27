from parser import detect_category, parse_expense, parse_income

def test_detect_category_food():
    assert detect_category("coffee") == "food"

def test_detect_category_groceries():
    assert detect_category("biedronka") == "groceries"

def test_detect_category_transport():
    assert detect_category("uber") == "transport"

def test_detect_category_other():
    assert detect_category("random unknown thing") == "other"

def test_parse_income():
    result = parse_income("salary 3000")

    assert result["name"] == "salary"
    assert result["amount"] == 3000
    assert result["type"] == "income"

def test_parse_expense():
    result = parse_expense("coffee 15")

    assert result["name"] == "coffee"
    assert result["amount"] == 15
    assert result["type"] == "expense"

def test_detect_category_services():
    assert detect_category("haircut") == "services"


def test_detect_category_education():
    assert detect_category("course") == "education"


def test_detect_category_bills():
    assert detect_category("internet") == "bills"


def test_parse_expense_with_multi_word_name():
    result = parse_expense("green tea 12.50")

    assert result["name"] == "green tea"
    assert result["amount"] == 12.50
    assert result["type"] == "expense"



def test_parse_expense_invalid_input():
    result = parse_expense("coffee")

    assert result is None


def test_parse_income_invalid_input():
    result = parse_income("salary")

    assert result is None

def test_parse_expense_decimal():
    result = parse_expense("tea 10.99")

    assert result["amount"] == 10.99


def test_parse_income_decimal():
    result = parse_income("salary 2500.50")

    assert result["amount"] == 2500.50


def test_parse_expense_negative():
    result = parse_expense("coffee -10")

    assert result is None


def test_parse_income_negative():
    result = parse_income("salary -500")

    assert result is None


def test_detect_category_case_insensitive():
    assert detect_category("UBER") == "transport"


def test_detect_category_polish_store():
    assert detect_category("biedronka") == "groceries"


def test_detect_category_restaurant():
    assert detect_category("pizza") == "food"
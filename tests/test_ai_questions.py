from ai import classify_message


def test_classify_question_english():
    result = classify_message(
        "how much did i spend this month"
    )

    assert result == "question"


def test_classify_question_russian():
    result = classify_message(
        "сколько я потратил за неделю"
    )

    assert result == "question"


def test_classify_question_polish():
    result = classify_message(
        "ile wydałem w tym miesiącu"
    )

    assert result == "question"


def test_classify_transaction():
    result = classify_message("coffee 15")

    assert result == "transaction"


def test_classify_category_question():
    result = classify_message(
        "how much did i spend on food this month"
    )

    assert result == "question"

def test_classify_biggest_expenses_question():
    result = classify_message(
        "what are my biggest expenses this month"
    )

    assert result == "question"

def test_classify_average_spending_question():
    result = classify_message(
        "what is my average daily spending this month"
    )

    assert result == "question"
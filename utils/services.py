from datetime import time, date
from transactions.models import Transaction


class Store:
    def __init__(
        self, name=None, transactions: list[Transaction] = [], balance=0
    ) -> None:
        self.name = name
        self.transactions: list[Transaction] = transactions
        self.balance = balance


def formatting_date(date_str: str):
    return date(
        year=int(date_str[:4]),
        month=int(date_str[4:6]),
        day=int(date_str[6:]),
    )


def formatting_time(time_str: str):
    return time(
        hour=int(time_str[:2]),
        minute=int(time_str[2:4]),
        second=int(time_str[4:]),
    )


def get_values_from_file(file):
    expected_fields = [
        {"name": "tipo_id", "start": 0, "end": 1},
        {"name": "data", "start": 1, "end": 9, "formatting": formatting_date},
        {"name": "valor", "start": 9, "end": 19},
        {"name": "cpf", "start": 19, "end": 30},
        {"name": "cartao", "start": 30, "end": 42},
        {"name": "hora", "start": 42, "end": 48, "formatting": formatting_time},
        {"name": "dono", "start": 48, "end": 62},
        {"name": "nome", "start": 62, "end": 81},
    ]

    lines = file.readlines()

    transaction_data_list = []

    for line in lines:
        transaction_data = {}

        for field in expected_fields:
            byte: bytes = line[field["start"] : field["end"]]
            formated_string = byte.decode("utf8").lstrip().rstrip()

            if field.get("formatting", None):
                function = field["formatting"]
                formated_string = function(formated_string)

            transaction_data[field["name"]] = formated_string

        transaction_data_list.append(transaction_data)

    return transaction_data_list


def create_stores(queryset, transaction_groups: list[Store]):
    for transaction in queryset:
        store_name_list = [store.name for store in transaction_groups]

        if not transaction.nome in store_name_list:
            new_store = Store(transaction.nome)
            transaction_groups.append(new_store)


def group_by_store(queryset):
    transaction_groups: list[Store] = []
    # # for transaction in queryset:
    # transaction.valor = round(transaction.valor / 100, 2)
    # transaction.hora = transaction.hora.strftime("%H:%M:%S")

    create_stores(queryset, transaction_groups)

    for store in transaction_groups:
        # resolvido bug das transactions
        store.transactions = []
        for transaction in queryset:
            if store.name == transaction.nome:
                store.transactions.append(transaction)

        for transaction in store.transactions:
            store.balance += (
                transaction.valor
                if transaction.tipo.sinal == "+"
                else -transaction.valor
            )

    return transaction_groups

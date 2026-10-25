from __future__ import annotations

from .database import Database


class StatementsDatabase(Database):
    def save_statement_imports(
        self,
        cards: list[dict],
        transactions: list[dict],
        month: str,
        year: str,
        source: str,
    ) -> int:
        if not cards:
            raise ValueError("At least one card is required")

        with self.conn:
            import_id = self._get_or_create_import(cards[0]["bank"], month, year, source)
            statement_ids = {
                index: self._get_or_create_statement(card, month, year, source, import_id)
                for index, card in enumerate(cards)
            }

            for statement_id in statement_ids.values():
                self._delete_statement_transactions(statement_id)

            self._save_transactions(transactions, statement_ids)

        return import_id

    def _get_or_create_import(self, bank: str, month: str, year: str, source: str) -> int:
        record = self.conn.execute(
            """SELECT id FROM statement_imports
               WHERE bank = ? AND statement_month = ?
               AND statement_year = ? AND source = ?""",
            (bank, month, year, source),
        ).fetchone()

        if record:
            import_id = record["id"]
            self.conn.execute(
                "UPDATE statement_imports SET imported_at = CURRENT_TIMESTAMP WHERE id = ?",
                (import_id,),
            )
            return import_id

        import_id = self.conn.execute(
            """INSERT INTO statement_imports
               (bank, statement_month, statement_year, source)
               VALUES (?, ?, ?, ?)""",
            (bank, month, year, source),
        ).lastrowid
        if import_id is None:
            raise RuntimeError("Could not create statement import")
        return import_id

    def _get_or_create_statement(
        self,
        card: dict,
        month: str,
        year: str,
        source: str,
        import_id: int,
    ) -> int:
        last4_digits = card.get("last4_digits", "")
        due_date = card.get("due_date")
        record = self.conn.execute(
            """SELECT id FROM statements
               WHERE bank = ? AND last4_digits = ?
               AND statement_month = ? AND statement_year = ?
               AND due_date IS ?""",
            (card["bank"], last4_digits, month, year, due_date),
        ).fetchone()

        values = (
            card["bank"],
            card["card"],
            last4_digits,
            card.get("loyalty_plan", ""),
            month,
            year,
            due_date,
            card.get("minimum_crc", 0),
            card.get("minimum_usd", 0),
            card.get("due_crc", 0),
            card.get("due_usd", 0),
            source,
            import_id,
        )

        if record:
            self.conn.execute(
                """UPDATE statements SET
                   bank = ?, card = ?, last4_digits = ?, loyalty_plan = ?,
                   statement_month = ?, statement_year = ?, due_date = ?,
                   minimum_crc = ?, minimum_usd = ?, due_crc = ?, due_usd = ?,
                   source = ?, import_id = ?
                   WHERE id = ?""",
                values + (record["id"],),
            )
            return record["id"]

        statement_id = self.conn.execute(
            """INSERT INTO statements
               (bank, card, last4_digits, loyalty_plan, statement_month,
                statement_year, due_date, minimum_crc, minimum_usd, due_crc,
                due_usd, source, import_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            values,
        ).lastrowid
        if statement_id is None:
            raise RuntimeError("Could not create statement")
        return statement_id

    def _delete_statement_transactions(self, statement_id: int) -> None:
        self.conn.execute(
            "DELETE FROM statement_transaction WHERE statement_id = ?",
            (statement_id,),
        )

    def _save_transactions(self, transactions: list[dict], statement_ids: dict[int, int]) -> None:
        default_statement_id = next(iter(statement_ids.values()))
        for transaction in transactions:
            statement_index = transaction.get("statement_index", 0)
            if not isinstance(statement_index, int):
                statement_index = 0
            statement_id = statement_ids.get(
                statement_index,
                default_statement_id,
            )
            self.conn.execute(
                """INSERT INTO statement_transaction
                   (statement_id, transaction_date, description, place, amount,
                    currency, source_card_last4, source_card_holder, assigned_to_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    statement_id,
                    transaction["transaction_date"],
                    transaction["description"],
                    transaction.get("place", ""),
                    transaction["amount"],
                    transaction["currency"],
                    transaction.get("source_card_last4", ""),
                    transaction.get("source_card_holder", transaction.get("source_cardholder", "")),
                    transaction.get("assigned_to_id"),
                ),
            )
            

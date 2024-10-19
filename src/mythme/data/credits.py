from datetime import datetime
from mythme.model.credit import Credit
from mythme.utils.db import get_connection


class CreditsData:
    select = """SELECT people.name, credits.role FROM credits
JOIN people ON credits.person = people.person
WHERE credits.chanid = %s
AND credits.starttime = %s
ORDER BY credits.priority"""

    def get_credits(self, channel_id: int, start: datetime) -> list[Credit]:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(CreditsData.select, [channel_id, start])
                return [self.to_credit(row) for row in cursor.fetchall()]

    def to_credit(self, row: dict) -> Credit:
        return Credit(name=row["name"], role=row["role"])

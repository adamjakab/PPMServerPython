#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  License: MIT

import sqlite3
from logging import Logger
from uuid import uuid4

class PPM_Storage:
    _config = {}
    _logger: Logger = None
    _conn = None
    _cursor = None

    def __init__(self, cfg, logger):
        self._config = cfg
        self._logger = logger
        self.setup_db()

    def _attribute_get(self, db_request):
        answer = {"error": False, "message": "ok."}

        user = db_request["user"] if "user" in db_request else ""
        card_id = db_request["card_id"] if "card_id" in db_request else ""
        key = db_request["key"] if "key" in db_request else ""
        kvm = {"user": user, "cid": card_id, "k": key}

        # Check if card is owned by user
        if not self._is_card_owned_by_user(card_id, user):
            answer.update({
                "error": True,
                "message": "There is no card by that id."
            })
            return answer

        sql = """SELECT ca.*
              FROM cards AS c
              INNER JOIN card_attributes AS ca on c.id = ca.card_id
              WHERE c.owner = :user
              AND c.id = :cid
              AND ca.key = :k
              """
        self._cursor.execute(sql, kvm)
        answer["data"] = self.get_json_from_cursor_data()

        return answer

    def _attribute_set(self, db_request):
        answer = {"error": False, "message": "ok."}

        user = db_request["user"] if "user" in db_request else ""
        card_id = db_request["card_id"] if "card_id" in db_request else ""
        key = db_request["key"] if "key" in db_request else ""
        value = db_request["value"] if "value" in db_request else ""
        kvm = {"user": user, "cid": card_id, "k": key, "v": value}

        # Check if card is owned by user
        if not self._is_card_owned_by_user(card_id, user):
            answer.update({
                "error": True,
                "message": "There is no card by that id."
            })
            return answer

        # Insert
        sql = """INSERT OR IGNORE 
                    INTO card_attributes (card_id, key, value)
                    VALUES(:cid,:k,:v)
        """
        self._cursor.execute(sql, kvm)

        # Update (ignore update if value has not changed)
        if self._cursor.rowcount == 0:
            kvm = {"cid": card_id, "k": key, "v": value}
            sql = """UPDATE OR IGNORE card_attributes SET
                        value = :v, 
                        modified = datetime('now', 'localtime')
                        WHERE card_id = :cid 
                        AND key = :k
                        AND value <> :v
                    """
            self._cursor.execute(sql, kvm)

        # Commit
        self._conn.commit()

        return self._attribute_get(db_request)

    def _attribute_delete(self, db_request):
        answer = {"error": False, "message": "ok."}

        user = db_request["user"] if "user" in db_request else ""
        card_id = db_request["card_id"] if "card_id" in db_request else ""
        key = db_request["key"] if "key" in db_request else ""
        kvm = {"cid": card_id, "k": key}

        # Check if card is owned by user
        if not self._is_card_owned_by_user(card_id, user):
            answer.update({
                "error": True,
                "message": "There is no card by that id."
            })
            return answer

        # Delete
        sql = """DELETE FROM card_attributes
                    WHERE card_id = :cid 
                    AND key = :k 
        """
        self._cursor.execute(sql, kvm)

        # Commit
        self._conn.commit()

        return answer

    def _cards_index(self, db_request):
        answer = {"error": False, "message": "ok."}

        user = db_request["user"] if "user" in db_request else ""
        kvm = {"user": user}
        sql = """SELECT c.*, COUNT(ca.key) AS attr_count
              FROM cards AS c
              LEFT OUTER JOIN card_attributes AS ca on c.id = ca.card_id
              WHERE c.owner = :user
              GROUP BY c.id
              ORDER BY c.modified DESC
              """
        self._cursor.execute(sql, kvm)
        answer["data"] = self.get_json_from_cursor_data()

        return answer

    def _card_get(self, db_request):
        answer = {"error": False, "message": "ok."}

        user = self._get_from_request(db_request, "user")
        card_id = self._get_from_request(db_request, "id")
        kvm = {"user": user, "card_id": card_id}

        # Check if card is owned by user
        if card_id and not self._is_card_owned_by_user(card_id, user):
            answer.update({
                "error": True,
                "message": "There is no card by that id."
            })
            return answer

        sql = """SELECT c.*, COUNT(ca.key) AS attr_count
                  FROM cards AS c
                  LEFT OUTER JOIN card_attributes AS ca on c.id = ca.card_id
                  WHERE c.id = :card_id
                  GROUP BY c.id
                      """
        self._cursor.execute(sql, kvm)
        answer["data"] = self.get_json_from_cursor_data()

        return answer

    def _card_set(self, db_request):
        answer = {"error": False, "message": "ok."}

        user = self._get_from_request(db_request, "user")
        card_id = self._get_from_request(db_request, "id")
        parent_id = self._get_from_request(db_request, "parent_id")
        collection = self._get_from_request(db_request, "collection")
        name = self._get_from_request(db_request, "name")
        identifier = self._get_from_request(db_request, "identifier")

        # Check if card is owned by user
        if card_id and not self._is_card_owned_by_user(card_id, user):
            answer.update({
                "error": True,
                "message": "There is no card by that id."
            })
            return answer

        # Insert
        if not card_id:
            card_id = self._get_from_request(db_request, "id", "AUTO")
            if not user:
                return {"error": True, "message": "User not set."}
            if not collection:
                return {"error": True, "message": "Collection not set."}
            if not name:
                return {"error": True, "message": "Name not set."}

            kvm = {"user": user, "card_id": card_id,
                   "parent_id": parent_id, "collection": collection,
                   "name": name, "identifier": identifier
                   }
            sql = """INSERT OR IGNORE 
                        INTO cards (id, parent_id, owner, collection, 
                        name, identifier)
                        VALUES(:card_id, :parent_id, :user, :collection, 
                        :name, :identifier)
                    """
            self._cursor.execute(sql, kvm)
            # Add card_id to db_request so that _card_get will load the new
            # card with the auto-generated id
            db_request["id"] = card_id
        else:
            # Update
            kvm = {"card_id": card_id, "parent_id": parent_id,
                   "name": name, "identifier": identifier
                   }
            sql = """UPDATE OR IGNORE cards SET {fields},
                        modified = datetime('now', 'localtime')
                        WHERE id = :card_id 
                    """
            fields = []
            if parent_id:
                fields.append("parent_id = :parent_id")
            if name:
                fields.append("name = :name")
            if identifier:
                fields.append("identifier = :identifier")

            if fields:

                sql = sql.format(fields=", ".join(fields))
                print(sql)
                self._cursor.execute(sql, kvm)

        # Commit
        self._conn.commit()

        return self._card_get(db_request)

    def _card_delete(self, db_request):
        answer = {"error": False, "message": "ok."}

        user = self._get_from_request(db_request, "user")
        card_id = self._get_from_request(db_request, "id")
        kvm = {"user": user, "card_id": card_id}

        # Check if card is owned by user
        if not self._is_card_owned_by_user(card_id, user):
            answer.update({
                "error": True,
                "message": "There is no card by that id."
            })
            return answer

        # Delete
        sql = """DELETE FROM cards
                    WHERE id = :card_id
        """
        self._cursor.execute(sql, kvm)

        # Commit
        self._conn.commit()

        return answer

    def handle_request_operation(self, db_request):
        db_response = {"request": db_request, "response": {}}
        if not "operation" in db_request:
            db_request["operation"] = ""

        if db_request["operation"] == "index":
            operation_response = self._cards_index(db_request)
        elif db_request["operation"] == "get_card":
            operation_response = self._card_get(db_request)
        elif db_request["operation"] == "set_card":
            operation_response = self._card_set(db_request)
        elif db_request["operation"] == "del_card":
            operation_response = self._card_delete(db_request)
        elif db_request["operation"] == "get_attribute":
            operation_response = self._attribute_get(db_request)
        elif db_request["operation"] == "set_attribute":
            operation_response = self._attribute_set(db_request)
        elif db_request["operation"] == "del_attribute":
            operation_response = self._attribute_delete(db_request)
        else:
            operation_response = {
                "error": True,
                "message": "Unknown operation requested."
            }

        db_response["response"].update(operation_response)

        return db_response

    def get_json_from_cursor_data(self):
        json_data = []

        headers = [x[0] for x in self._cursor.description]
        rows = self._cursor.fetchall()
        self._logger.debug("JSON got rows: {}".format(len(rows)))

        # if dataset is empty - cursor returns:
        # '[(None, None, None, None, None,None, None, None,...)]' nonsense
        if len(rows) and rows[0][0] is not None:
            for row in rows:
                json_data.append(dict(zip(headers, row)))

        return json_data

    def _is_card_owned_by_user(self, card_id, user):
        kvm = {"user": user, "cid": card_id}
        sql = """SELECT COUNT(c.id) AS cnt
                              FROM cards AS c
                              WHERE c.owner = :user
                              AND c.id = :cid
                              """
        self._cursor.execute(sql, kvm)
        data = self.get_json_from_cursor_data()
        record_count = int(data[0]["cnt"])
        return record_count == 1

    @staticmethod
    def _get_from_request(db_request, key, default=None):
        answer = db_request[key] if key in db_request else default
        if answer == default and answer == "AUTO":
            answer = str(uuid4())

        return answer

    def setup_db(self):
        db_file = self._config["DATABASE_FILE"]
        self._conn = sqlite3.connect(db_file)
        self._conn.execute("PRAGMA foreign_keys = 1")
        self._cursor = self._conn.cursor()

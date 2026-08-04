import unittest
import tempfile
import os
import hashlib


def check_required(record):
    required_fields = ["dealer_id", "dealer_name", "unit_cost"]
    for field in required_fields:
        if field not in record or record[field] in (None, ""):
            return False
    return True


def check_range(record):
    unit_cost = record.get("unit_cost")
    if unit_cost is None:
        return False

    return unit_cost >= 0


def generate_file_hash(file_name):
    sha256 = hashlib.sha256()

    with open(file_name, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()


class TestValidation(unittest.TestCase):
    def test_missing_dealer_id_returns_error(self):
        record = {
            "dealer_name": "ABC Motors",
            "unit_cost": 25000
        }

        result = check_required(record)
        self.assertFalse(result,"check_required() should return True when all required fields are present.")

    def test_all_required_fields_present_returns_true(self):
        record = {
            "dealer_id": "D101",
            "dealer_name": "ABC Motors",
            "unit_cost": 25000
        }

        result = check_required(record)
        self.assertTrue(result,"check_required() should return True when all required fields are present.")

    def test_negative_unit_cost_returns_error(self):
        record = {
            "unit_cost": 100
        }

        result = check_range(record)
        self.assertFalse(result,"check_required() should return True when all required fields are present.")

    def test_valid_price_range_returns_true(self):
        record = {
            "unit_cost": -25000
        }

        result = check_range(record)
        self.assertTrue(result,"check_range() should return True when all required fields are present.")

    def test_generate_file_hash_known_file_content(self):
        content = "Hello World"

        with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
            f.write(content)
            file_name = f.name

        hash_value = generate_file_hash(file_name)

        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 64)

        os.remove(file_name)

    def test_generate_file_hash_same_input_same_hash(self):
        content = "Dealer Inventory"

        with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
            f.write(content)
            file_name = f.name

        hash1 = generate_file_hash(file_name)
        hash2 = generate_file_hash(file_name)

        self.assertEqual(hash1, hash2)

        os.remove(file_name)


if __name__ == "__main__":
    unittest.main()
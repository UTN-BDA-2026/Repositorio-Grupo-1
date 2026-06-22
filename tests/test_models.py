import unittest

from pydantic import ValidationError

from app.models.habit import HabitCreate, HabitResponse


class HabitModelsTests(unittest.TestCase):
    # Valida reglas de entrada y serialización de modelos de hábitos.
    def test_habit_create_valid_payload(self):
        habit = HabitCreate(name="Leer", frequency="daily", status="active")
        self.assertEqual(habit.name, "Leer")
        self.assertEqual(habit.status, "active")

    def test_habit_create_rejects_extra_fields(self):
        with self.assertRaises(ValidationError):
            HabitCreate(
                name="Leer",
                frequency="daily",
                status="active",
                injected={"$ne": None},
            )

    def test_habit_create_rejects_invalid_status(self):
        with self.assertRaises(ValidationError):
            HabitCreate(name="Leer", frequency="daily", status="invalid")

    def test_habit_create_rejects_empty_frequency(self):
        with self.assertRaises(ValidationError):
            HabitCreate(name="Leer", frequency="", status="active")

    def test_habit_create_rejects_too_long_frequency(self):
        with self.assertRaises(ValidationError):
            HabitCreate(name="Leer", frequency="x" * 61, status="active")

    def test_habit_response_maps_mongo_id_alias(self):
        response = HabitResponse(_id="abc123", name="Leer", frequency="daily", status="active")
        dumped = response.model_dump()
        self.assertEqual(dumped["id"], "abc123")
        self.assertNotIn("_id", dumped)


if __name__ == "__main__":
    unittest.main()

import asyncio
import unittest


class MainTests(unittest.TestCase):
    # Comprueba respuesta esperada del endpoint de salud.
    def test_health_endpoint_function(self):
        from main import health

        result = asyncio.run(health())
        self.assertEqual(result, {"status": "ok"})


if __name__ == "__main__":
    unittest.main()

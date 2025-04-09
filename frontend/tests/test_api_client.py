import unittest
from unittest.mock import patch, Mock
import requests
from frontend.api_client import get_answer, get_preferences, post_preferences, put_preference

class TestAPIHandler(unittest.TestCase):

    @patch("requests.get")
    def test_get_answer_success(self, mock_get):
        """Testet eine erfolgreiche Antwort von der API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"answer": "Das ist die Antwort"}
        mock_get.return_value = mock_response

        result = get_answer("Testfrage")
        self.assertEqual(result, "Das ist die Antwort")
        mock_get.assert_called_once_with("http://api:8000/answer", params={"message": "Testfrage"})

    @patch("requests.get")
    def test_get_answer_failure(self, mock_get):
        """Testet eine fehlgeschlagene API-Anfrage."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = get_answer("Testfrage")
        self.assertEqual(result, "500: Fehler bei der Anfrage an die API.")

    @patch("requests.get", side_effect=requests.RequestException)
    def test_get_answer_exception(self, mock_get):
        """Testet eine fehlgeschlagene API-Anfrage (Netzwerkfehler)."""
        result = get_answer("Testfrage")
        self.assertEqual(result, "Ich kann mich gerade nicht mit der API verbinden.")

    @patch("requests.get")
    def test_get_preferences_success(self, mock_get):
        """Testet eine erfolgreiche Abfrage der Benutzerpräferenzen."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "course": "IN22",
            "cafeteria": "Mensa Central",
            "city": "Berlin",
            "preferred_transport_medium": "Fahrrad",
            "stocks": ["Tesla", "Apple"],
            "news": ["BBC", "CNN"]
        }
        mock_get.return_value = mock_response

        summary, status = get_preferences(1234)
        self.assertIn("📚 Kurs: IN22", summary)
        self.assertEqual(status, "success")

    @patch("requests.get")
    def test_get_preferences_failure(self, mock_get):
        """Testet eine fehlgeschlagene Anfrage für Präferenzen."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        summary, status = get_preferences(1234)
        self.assertEqual(status, "error")
        self.assertIn("404: Fehler bei der Anzeige der Präferenzen.", summary)

    @patch("requests.get", side_effect=requests.RequestException)
    def test_get_preferences_exception(self, mock_get):
        """Testet einen Netzwerkfehler bei Präferenzen."""
        summary, status = get_preferences(1234)
        self.assertEqual(status, "error")
        self.assertEqual(summary, "Ich kann gerade deine Präferenzen nicht abrufen.")

    @patch("requests.post")
    def test_post_preferences_success(self, mock_post):
        """Testet eine erfolgreiche Speicherung von Präferenzen."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = post_preferences(1234, {
            "kurs": "IN22",
            "mensa": "Mensa Central",
            "wohnort": "Berlin",
            "transport": "Fahrrad",
            "aktien": ["Tesla", "Apple"],
            "news": ["BBC", "CNN"]
        })
        self.assertEqual(result, "Deine Präferenzen wurden erfolgreich gespeichert.")

    @patch("requests.post")
    def test_post_preferences_failure(self, mock_post):
        """Testet einen Fehler beim Speichern von Präferenzen."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        result = post_preferences(1234, {})
        self.assertEqual(result, "400: Fehler bei der Anfrage an die API.")

    @patch("requests.post", side_effect=requests.RequestException)
    def test_post_preferences_exception(self, mock_post):
        """Testet eine fehlerhafte Verbindung bei post_preferences."""
        result = post_preferences(1234, {})
        self.assertEqual(result, "Du hast deine Präferenzen anscheinend schon initialisiert.")

    @patch("requests.get")
    @patch("requests.put")
    def test_put_preference_success(self, mock_put, mock_get):
        """Testet ein erfolgreiches Aktualisieren einer Präferenz."""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"course": "IN22"}
        mock_get.return_value = mock_get_response

        mock_put_response = Mock()
        mock_put_response.status_code = 200
        mock_put.return_value = mock_put_response

        result = put_preference(1234, "course", "IN23")
        self.assertEqual(result, "Deine Präferenz wurde erfolgreich aktualisiert.")
        mock_put.assert_called_once()

    @patch("requests.get")
    @patch("requests.put")
    def test_put_preference_invalid_key(self, mock_put, mock_get):
        """Testet das Aktualisieren einer ungültigen Präferenz."""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"course": "IN22"}
        mock_get.return_value = mock_get_response

        result = put_preference(1234, "invalid_key", "test")
        self.assertEqual(result, "Ungültige Präferenz: invalid_key")
        mock_put.assert_not_called()

    @patch("requests.get")
    @patch("requests.put")
    def test_put_preference_failure(self, mock_put, mock_get):
        """Testet eine fehlgeschlagene Aktualisierung."""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"course": "IN22"}
        mock_get.return_value = mock_get_response

        mock_put_response = Mock()
        mock_put_response.status_code = 400
        mock_put.return_value = mock_put_response

        result = put_preference(1234, "course", "IN23")
        self.assertEqual(result, "Fehler bei der Aktualisierung: 400")

    @patch("requests.get", side_effect=requests.RequestException)
    def test_put_preference_get_exception(self, mock_get):
        """Testet eine fehlgeschlagene Verbindung beim Abrufen der Präferenz."""
        result = put_preference(1234, "course", "IN23")
        self.assertEqual(result, "Ich kann gerade deine Präferenz nicht ändern.")

if __name__ == "__main__":
    unittest.main()

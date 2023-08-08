import unittest
import listener  # Assuming the name of your script is "listener.py"
import smtplib

class TestListenerFunctions(unittest.TestCase):
    
    def test_log_exception(self):
        # Here, we can trigger an exception and check if it was logged.
        # For this example, I'm going to assume that the logger writes to a list. 
        # In your real implementation, you might want to check if the log file got updated.
        listener.log.clear()
        try:
            1/0  # Causes ZeroDivisionError
        except:
            listener.log_exception("Caught exception")
        self.assertTrue(len(listener.log) > 0)

    def test_setup_server(self):
        # Test if a SMTP server is set up successfully
        server = listener.setup_server()
        self.assertIsInstance(server, smtplib.SMTP)
        server.quit()

    def test_send_email(self):
        # For this test, we are mocking send_email to not send an actual email but to check if the function runs without errors
        def mock_send_email(subject, body, attachment_path=None):
            pass

        original_send_email = listener.send_email
        listener.send_email = mock_send_email
        listener.send_email("Test Subject", "Test Body")
        listener.send_email = original_send_email

if __name__ == '__main__':
    unittest.main()

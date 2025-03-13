import unittest
import os
import coverage

def discover_and_run_tests():
    # Initialisiere Coverage
    cov = coverage.Coverage(source=["backend","frontend"], omit=["*/test_*"])
    cov.start()

    # Suche alle Dateien, die mit 'test_' beginnen
    test_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    
    # Lade alle Tests mit unittest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for test_file in test_files:
        # Füge jede Test-Datei zum Test-Suite hinzu
        suite.addTests(loader.discover(os.path.dirname(test_file), pattern=os.path.basename(test_file)))
    
    # Führe die Tests aus
    runner = unittest.TextTestRunner()
    runner.run(suite)

    # Stoppe Coverage und gib das Ergebnis aus
    cov.stop()
    cov.save()
    cov.report()

if __name__ == "__main__":
    discover_and_run_tests()

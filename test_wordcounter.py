from report_generator import TestReportGenerator
from test_scenarios import (
    tc_01_standard_counting,
    tc_02_empty_text,
    tc_03_multiple_spaces,
    tc_04_special_chars,
    tc_05_case_sensitivity,
    tc_06_intentional_failure
)

if __name__ == "__main__":
    reporter = TestReportGenerator(output_dir="reports")

    scenarios = [
        (
            "TC-001",
            "Conteo estándar y Top Keyword Density",
            tc_01_standard_counting,
            "farma farmatodo farma todo todo farma",
            {
                "words": 6, 
                "characters": 37,
                "keywords": [
                    {"word": "farma", "count": 3},
                    {"word": "todo", "count": 2},
                    {"word": "farmatodo", "count": 1}
                ]
            }
        ),
        (
            "TC-002",
            "Caja de texto vacía",
            tc_02_empty_text,
            "",
            {
                "words": 0, 
                "characters": 0,
                "keywords": []
            }
        ),
        (
            "TC-003",
            "Espacios múltiples y saltos de línea",
            tc_03_multiple_spaces,
            "   farmatodo    \n\n   calidad \t\t software   ",
            {
                "words": 3, 
                "characters": 43,
                "keywords": [
                    {"word": "farmatodo", "count": 1},
                    {"word": "calidad", "count": 1},
                    {"word": "software", "count": 1}
                ]
            }
        ),
        (
            "TC-004",
            "Caracteres especiales",
            tc_04_special_chars,
            "!!! @@@ ### $$$ %%% ^^^ ***",
            {
                "words": 0,
                "characters": 27,
                "keywords": []
            }
        ),
        (
            "TC-005",
            "Keysensitive a mayúsculas/minúsculas",
            tc_05_case_sensitivity,
            "Farmatodo FARMATODO farmatodo Farmatodo",
            {
                "words": 4,
                "characters": 39,
                "keywords": [
                    {"word": "farmatodo", "count": 4}
                ]
            }
        ),
        (
            "TC-006",
            "Escenario de fallo controlado",
            tc_06_intentional_failure,
            "farmatodo automatizacion qa",
            {
                "words": 999,  
                "characters": 27,
                "keywords": []
            }
        )
    ]

    print("[INFO] Ejecutando suite de pruebas automatizadas con Playwright...")
    reporter.run_suite(scenarios)
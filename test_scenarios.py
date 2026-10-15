import time

def extract_keyword_density(page):
    keywords = []
    try:
        page.wait_for_selector("#kwd-accordion-data, .card-body", timeout=3000)
        # Seleccionamos las filas o elementos del panel de densidad
        items = page.locator("#kwd-accordion-data .row, #kwd-accordion-data .list-group-item, div[id*='kwd'] .d-flex").all()
        
        for item in items[:3]:
            txt = item.inner_text().strip()
            if txt:
                lines = txt.split("\n")
                if len(lines) >= 2:
                    word = lines[0].strip()
                    count_raw = lines[1].strip().split()[0]
                    count_str = ''.join(filter(str.isdigit, count_raw))
                    count = int(count_str) if count_str else 0
                    if not word.endswith('%') and word:
                        keywords.append({"word": word, "count": count})
    except Exception:
        pass
    return keywords

def tc_01_standard_counting(page, input_text, expected_data, steps_evidence, actual_data):
    text_area = page.locator("#box")
    text_area.click()
    text_area.clear()
    text_area.fill(input_text)
    time.sleep(1.0) 

    words_val = page.locator("#word_count").text_content().strip()
    chars_val = page.locator("#character_count").text_content().strip()

    actual_data["words"] = int(words_val.replace(",", ""))
    actual_data["characters"] = int(chars_val.replace(",", ""))
    actual_data["keywords"] = extract_keyword_density(page)

    steps_evidence.append({
        "desc": "Conteo de palabras",
        "expected": expected_data["words"],
        "actual": actual_data["words"],
        "passed": actual_data["words"] == expected_data["words"]
    })
    steps_evidence.append({
        "desc": "Conteo de caracteres",
        "expected": expected_data["characters"],
        "actual": actual_data["characters"],
        "passed": actual_data["characters"] == expected_data["characters"]
    })

    assert actual_data["words"] == expected_data["words"], f"Esperado {expected_data['words']} palabras, obtenido {actual_data['words']}"
    assert actual_data["characters"] == expected_data["characters"], f"Esperado {expected_data['characters']} caracteres, obtenido {actual_data['characters']}"

def tc_02_empty_text(page, input_text, expected_data, steps_evidence, actual_data):
    text_area = page.locator("#box")
    text_area.click()
    text_area.clear()
    time.sleep(0.5)

    words_val = page.locator("#word_count").text_content().strip()
    chars_val = page.locator("#character_count").text_content().strip()

    actual_data["words"] = int(words_val.replace(",", ""))
    actual_data["characters"] = int(chars_val.replace(",", ""))
    actual_data["keywords"] = []

    steps_evidence.append({
        "desc": "Conteo con caja vacía",
        "expected": expected_data["words"],
        "actual": actual_data["words"],
        "passed": actual_data["words"] == 0
    })

    assert actual_data["words"] == 0
    assert actual_data["characters"] == 0

def tc_03_multiple_spaces(page, input_text, expected_data, steps_evidence, actual_data):
    text_area = page.locator("#box")
    text_area.click()
    text_area.clear()
    text_area.fill(input_text)
    time.sleep(1.0)

    words_val = page.locator("#word_count").text_content().strip()
    chars_val = page.locator("#character_count").text_content().strip()

    actual_data["words"] = int(words_val.replace(",", ""))
    actual_data["characters"] = int(chars_val.replace(",", ""))
    actual_data["keywords"] = extract_keyword_density(page)

    steps_evidence.append({
        "desc": "Palabras con espacios múltiples",
        "expected": expected_data["words"],
        "actual": actual_data["words"],
        "passed": actual_data["words"] == expected_data["words"]
    })

    assert actual_data["words"] == expected_data["words"]

def tc_04_special_chars(page, input_text, expected_data, steps_evidence, actual_data):
    text_area = page.locator("#box")
    text_area.click()
    text_area.clear()
    text_area.fill(input_text)
    time.sleep(1.0)

    words_val = page.locator("#word_count").text_content().strip()
    chars_val = page.locator("#character_count").text_content().strip()

    actual_data["words"] = int(words_val.replace(",", ""))
    actual_data["characters"] = int(chars_val.replace(",", ""))
    actual_data["keywords"] = extract_keyword_density(page)

    steps_evidence.append({
        "desc": "Palabras en solo símbolos",
        "expected": expected_data["words"],
        "actual": actual_data["words"],
        "passed": actual_data["words"] == expected_data["words"]
    })

    assert actual_data["words"] == expected_data["words"]

def tc_05_case_sensitivity(page, input_text, expected_data, steps_evidence, actual_data):
    text_area = page.locator("#box")
    text_area.click()
    text_area.clear()
    text_area.fill(input_text)
    time.sleep(1.0)

    words_val = page.locator("#word_count").text_content().strip()
    chars_val = page.locator("#character_count").text_content().strip()

    actual_data["words"] = int(words_val.replace(",", ""))
    actual_data["characters"] = int(chars_val.replace(",", ""))
    actual_data["keywords"] = extract_keyword_density(page)

    steps_evidence.append({
        "desc": "Conteo variantes capitalización",
        "expected": expected_data["words"],
        "actual": actual_data["words"],
        "passed": actual_data["words"] == expected_data["words"]
    })

    assert actual_data["words"] == expected_data["words"]

def tc_06_intentional_failure(page, input_text, expected_data, steps_evidence, actual_data):
    text_area = page.locator("#box")
    text_area.click()
    text_area.clear()
    text_area.fill(input_text)
    time.sleep(1.0)

    words_val = page.locator("#word_count").text_content().strip()
    chars_val = page.locator("#character_count").text_content().strip()

    actual_data["words"] = int(words_val.replace(",", ""))
    actual_data["characters"] = int(chars_val.replace(",", ""))
    actual_data["keywords"] = extract_keyword_density(page)

    steps_evidence.append({
        "desc": "Validación con fallo forzado de demostración",
        "expected": expected_data["words"],
        "actual": actual_data["words"],
        "passed": actual_data["words"] == expected_data["words"]
    })

    assert actual_data["words"] == expected_data["words"], f"[FAIL] Caso de error intencional: esperado {expected_data['words']} palabras, pero se obtuvo {actual_data['words']}."
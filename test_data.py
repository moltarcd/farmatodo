import hashlib
from playwright.sync_api import expect

URL = "https://wordcounter.net/"

def generate_short_hash(text):
    if not text:
        return "e3b0c44298fc"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

def fill_text(page, text: str):
    page.wait_for_load_state("domcontentloaded")
    
    editor = page.locator("#box, textarea#box, div[contenteditable='true']").first
    expect(editor).to_be_visible(timeout=15000)
    
    try:
        editor.click(timeout=3000)
    except:
        editor.click(force=True)

    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    
    if text:
        if len(text) > 1000:
            editor.focus()
            page.evaluate(f"""
                (() => {{
                    const box = document.querySelector('#box');
                    if (box) {{
                        const textData = {repr(text)};
                        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")?.set;
                        
                        if (nativeSetter) {{
                            nativeSetter.call(box, textData);
                        }} else {{
                            box.value = textData;
                        }}
                        
                        box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        box.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }})();
            """)
            page.wait_for_timeout(3000) 
        else:

            editor.fill(text)
            page.evaluate("""
                const box = document.querySelector('#box');
                if (box) {
                    box.dispatchEvent(new Event('input', { bubbles: true }));
                    box.dispatchEvent(new Event('change', { bubbles: true }));
                }
            """)
            page.wait_for_timeout(1000)

def read_counts(page):
    word_elem = page.locator("#word_count")
    char_elem = page.locator("#character_count")
    
    try:
        word_elem.wait_for(state="attached", timeout=5000)
    except:
        pass
        
    w = word_elem.inner_text().strip()
    c = char_elem.inner_text().strip()
    return w, c

def read_density(page, n=3):
    keywords = []
    items = page.locator("#kwd-accordion-data .list-group-item, tr.keyword-row, ul.top-keywords li").all()
    for item in items[:n]:
        keywords.append(item.inner_text().strip().lower())
    return keywords
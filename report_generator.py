import os
import time
import traceback
from datetime import datetime
from playwright.sync_api import sync_playwright
from test_data import URL, generate_short_hash

class TestReportGenerator:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.artifacts_dir = os.path.join(self.output_dir, f"artifacts_{self.run_id}")
        os.makedirs(self.artifacts_dir, exist_ok=True)
        self.results = []
        self.start_time_global = time.time()

    def run_suite(self, scenarios_list):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            for test_id, test_name, test_func, input_text, expected_data in scenarios_list:
                context.tracing.start(screenshots=True, snapshots=True, sources=True)
                page = context.new_page()

                console_logs = []
                page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
                page.on("pageerror", lambda err: console_logs.append(f"[error] {str(err)}"))

                http_response_info = {"url": "", "status": 0}
                def handle_response(response):
                    if "wordcounter.net" in response.url:
                        http_response_info["url"] = response.url
                        http_response_info["status"] = response.status
                page.on("response", handle_response)

                start_ts = datetime.utcnow()
                start_time_ms = time.time()
                status = "PASSED"
                error_msg = "-"
                stacktrace_str = "-"
                actual_data = {"words": 0, "characters": 0, "keywords": []}
                steps_evidence = []
                screenshot_rel_path = None

                try:
                    page.goto(URL, wait_until="domcontentloaded")
                    test_func(page, input_text, expected_data, steps_evidence, actual_data)
                    duration_ms = int((time.time() - start_time_ms) * 1000)
                    end_ts = datetime.utcnow()
                except AssertionError as ae:
                    status = "FAILED"
                    error_msg = str(ae)
                    stacktrace_str = traceback.format_exc()
                    duration_ms = int((time.time() - start_time_ms) * 1000)
                    end_ts = datetime.utcnow()
                except Exception as e:
                    status = "ERROR"
                    error_msg = str(e)
                    stacktrace_str = traceback.format_exc()
                    duration_ms = int((time.time() - start_time_ms) * 1000)
                    end_ts = datetime.utcnow()

                # Tomar captura de pantalla para TODOS los escenarios (Passed, Failed y Error)
                try:
                    safe_name = f"{test_id}_{test_name.lower().replace(' ', '_').replace('·', '')}.png"
                    screenshot_filename = "".join([c for c in safe_name if c.isalnum() or c in ('_', '.', '-')])
                    screenshot_abs_path = os.path.join(self.artifacts_dir, screenshot_filename)
                    page.screenshot(path=screenshot_abs_path, full_page=True)
                    screenshot_rel_path = f"artifacts_{self.run_id}/{screenshot_filename}"
                except Exception:
                    pass

                trace_filename = f"{test_id}_trace.zip"
                trace_path = os.path.join(self.artifacts_dir, trace_filename)
                context.tracing.stop(path=trace_path)

                self.results.append({
                    "id": test_id,
                    "name": test_name,
                    "status": status,
                    "start_time": start_ts.isoformat(),
                    "end_time": end_ts.isoformat(),
                    "duration_ms": duration_ms,
                    "input_text": input_text,
                    "input_length": len(input_text),
                    "input_hash": generate_short_hash(input_text),
                    "expected": expected_data,
                    "actual": actual_data,
                    "steps": steps_evidence,
                    "error": error_msg,
                    "stacktrace": stacktrace_str,
                    "url_final": http_response_info["url"] or page.url,
                    "http_status": http_response_info["status"] or 200,
                    "console_logs": console_logs,
                    "screenshot": screenshot_rel_path,
                    "trace_file": f"artifacts_{self.run_id}/{trace_filename}"
                })

                page.close()

            browser.close()
        
        self._build_html_report()

    def _build_html_report(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASSED")
        failed = sum(1 for r in self.results if r["status"] == "FAILED")
        error_count = sum(1 for r in self.results if r["status"] == "ERROR")
        total_duration = int((time.time() - self.start_time_global))
        efectividad = round((passed / total * 100), 1) if total > 0 else 0

        # Construcción modular de filas de índice y detalles
        index_rows_html = ""
        for r in self.results:
            badge_class = f"badge-{r['status'].lower()}"
            err_preview = (r["error"][:80] + "...") if len(r["error"]) > 80 else r["error"]
            index_rows_html += f"""
            <tr>
              <td><a href='#test-{r['id']}'>{r['id']}</a></td>
              <td>{r['name']}</td>
              <td><span class='badge {badge_class}'>{r['status']}</span></td>
              <td>{r['duration_ms']} ms</td>
              <td class='err'>{err_preview}</td>
            </tr>
            """

        details_html = ""
        for r in self.results:
            badge_class = f"badge-{r['status'].lower()}"
            preview_text = (r['input_text'][:60] + "...") if len(r['input_text']) > 60 else (r['input_text'] or "-")
            
            steps_rows = ""
            if r["steps"]:
                for step in r["steps"]:
                    status_col = "<span class='ok'>OK</span>" if step.get("passed", True) else "<span class='ko'>KO</span>"
                    steps_rows += f"<tr><td>{step.get('desc')}</td><td class='v'>{step.get('expected')}</td><td class='v'>{step.get('actual')}</td><td>{status_col}</td></tr>"

            steps_block = f"""
            <div class="block">
              <h4>Evidencia de pasos</h4>
              <table class="steps">
                <thead><tr><th>Comprobación</th><th>Esperado</th><th>Obtenido</th><th></th></tr></thead>
                <tbody>{steps_rows}</tbody>
              </table>
            </div>""" if steps_rows else ""

            # Procesamiento de Keyword Density
            expected_kw = r["expected"].get("keywords", []) if isinstance(r["expected"], dict) else []
            actual_kw = r["actual"].get("keywords", []) if isinstance(r["actual"], dict) else []
            
            def format_kw_list(kw_list):
                if not kw_list:
                    return "Sin datos de palabras clave"
                formatted = []
                for item in kw_list:
                    if isinstance(item, dict):
                        w = item.get("word", "")
                        c = item.get("count", 0)
                        formatted.append(f"• <b>{w}</b>: {c} reps")
                    elif isinstance(item, (list, tuple)) and len(item) == 2:
                        formatted.append(f"• <b>{item[0]}</b>: {item[1]} reps")
                return "<br>".join(formatted) if formatted else "Formato no válido"

            kw_expected_str = format_kw_list(expected_kw)
            kw_actual_str = format_kw_list(actual_kw)

            keyword_density_block = f"""
            <div class="block">
              <h4>Densidad de Palabras Clave (Top 3 Keyword Density)</h4>
              <div class="kv">
                <div class="k">Esperado (Top 3)</div>
                <div class="v keyword-box">{kw_expected_str}</div>
                <div class="k">Obtenido (Top 3 UI)</div>
                <div class="v keyword-box">{kw_actual_str}</div>
              </div>
            </div>"""

            error_block = ""
            if r["status"] != "PASSED":
                error_block = f"""
            <div class="block">
              <h4>Error</h4>
              <pre>{r['error']}</pre>
              <h4>Stacktrace</h4><pre>{r['stacktrace']}</pre>
            </div>"""

            screenshot_block = ""
            if r["screenshot"]:
                screenshot_block = f"""
            <div class="block">
              <h4>Captura de pantalla (Evidencia Visual)</h4>
              <a href="{r['screenshot']}" target="_blank">
                <img class="shot" src="{r['screenshot']}" alt="screenshot">
              </a>
            </div>"""

            console_block = ""
            if r["console_logs"]:
                logs_str = "\n".join(r["console_logs"])
                console_block = f"""
            <div class="block">
              <h4>Consola del Navegador</h4>
              <pre class="console">{logs_str}</pre>
            </div>"""

            trace_block = f"""
            <div class="block">
              <h4>Trazas Playwright</h4>
              <div class="kv">
                <div class="k">Archivo ZIP</div>
                <div class="v"><a href="{r['trace_file']}" download>Descargar Trace (.zip)</a> (Ejecutar: <code>playwright show-trace {r['trace_file']}</code>)</div>
              </div>
            </div>"""

            details_html += f"""
            <details id="test-{r['id']}">
              <summary>
                <span class="badge {badge_class}">{r['status']}</span>
                <span class="summary-name">{r['id']} · {r['name']}</span>
                <span class="summary-dur">{r['duration_ms']} ms</span>
              </summary>
              
              <div class="block">
                <h4>Contexto</h4>
                <div class="kv">
                  <div class="k">ID</div><div class="v">{r['id']}</div>
                  <div class="k">Inicio</div><div class="v">{r['start_time']}</div>
                  <div class="k">Fin</div><div class="v">{r['end_time']}</div>
                  <div class="k">Duración</div><div class="v">{r['duration_ms']} ms</div>
                  <div class="k">URL final</div><div class="v">{r['url_final']} (HTTP {r['http_status']})</div>
                </div>
              </div>
              
              <div class="block">
                <h4>Entrada enviada</h4>
                <div class="kv">
                  <div class="k">Preview</div><div class="v">{preview_text}</div>
                  <div class="k">Longitud</div><div class="v">{r['input_length']}</div>
                  <div class="k">SHA256</div><div class="v">{r['input_hash']}</div>
                </div>
              </div>
              
              {steps_block}
              {keyword_density_block}
              {error_block}
              {screenshot_block}
              {console_block}
              {trace_block}
            </details>
            """

        # HTML maestro limpio
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reporte de pruebas · Farmatodo QA · wordcounter.net · {self.run_id}</title>
<style>
  :root {{
    --c-blue:#0076CE; --c-pass:#28a745; --c-fail:#dc3545;
    --c-err:#fd7e14; --c-skip:#6c757d; --c-bg:#f4f7f6; --c-line:#e3e6e8;
  }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', Roboto, Arial, sans-serif; margin:0; padding:24px;
         background:var(--c-bg); color:#222; font-size:14px; }}
  .container {{ max-width:1100px; margin:auto; background:#fff; padding:28px 32px;
                border-radius:10px; box-shadow:0 4px 18px rgba(0,0,0,.06); }}
  h1 {{ margin:0 0 6px; color:var(--c-blue); font-size:22px; }}
  h2 {{ color:#333; margin-top:32px; border-bottom:2px solid var(--c-line); padding-bottom:6px; }}
  .meta {{ color:#666; font-size:13px; margin-bottom:20px; }}
  .kpis {{ display:grid; grid-template-columns:repeat(6,1fr); gap:12px; margin:20px 0 28px; }}
  .kpi {{ background:#f8f9fb; border-left:4px solid var(--c-blue); border-radius:6px;
          padding:14px; text-align:center; }}
  .kpi.pass {{ border-left-color:var(--c-pass); }}
  .kpi.fail {{ border-left-color:var(--c-fail); }}
  .kpi.err  {{ border-left-color:var(--c-err); }}
  .kpi.skip {{ border-left-color:var(--c-skip); }}
  .kpi .v {{ font-size:22px; font-weight:700; }}
  .kpi .l {{ font-size:11px; color:#666; text-transform:uppercase; letter-spacing:.04em; }}
  table {{ width:100%; border-collapse:collapse; margin-top:8px; }}
  th, td {{ padding:10px 12px; text-align:left; border-bottom:1px solid var(--c-line); vertical-align:top; }}
  th {{ background:var(--c-blue); color:#fff; font-weight:600; }}
  tr:hover td {{ background:#f6f8fa; }}
  .badge {{ display:inline-block; padding:3px 10px; border-radius:12px; font-size:11px;
            font-weight:700; color:#fff; letter-spacing:.03em; }}
  .badge-passed  {{ background:var(--c-pass); }}
  .badge-failed  {{ background:var(--c-fail); }}
  .badge-error   {{ background:var(--c-err); }}
  .err {{ color:var(--c-fail); font-family: ui-monospace, Consolas, monospace; font-size:12px; }}
  details {{ margin:14px 0; border:1px solid var(--c-line); border-radius:8px; background:#fff; }}
  details > summary {{ cursor:pointer; padding:12px 16px; font-weight:600; list-style:none;
                       display:flex; align-items:center; gap:12px; }}
  details > summary::-webkit-details-marker {{ display:none; }}
  details[open] > summary {{ border-bottom:1px solid var(--c-line); background:#f8f9fb; }}
  .summary-name {{ flex:1; }}
  .summary-dur {{ color:#666; font-weight:400; font-size:12px; }}
  .block {{ padding:16px 20px; border-top:1px dashed var(--c-line); }}
  .block:first-of-type {{ border-top:none; }}
  .block h4 {{ margin:0 0 8px; font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:#555; }}
  .kv {{ display:grid; grid-template-columns: 180px 1fr; gap:6px 16px; font-size:13px; }}
  .kv .k {{ color:#666; }}
  .kv .v {{ font-family: ui-monospace, Consolas, monospace; word-break:break-word; }}
  table.steps th, table.steps td {{ font-size:12.5px; }}
  .ok {{ color:var(--c-pass); font-weight:700; }}
  .ko {{ color:var(--c-fail); font-weight:700; }}
  pre {{ background:#0f172a; color:#e5e7eb; padding:12px 14px; border-radius:6px;
         overflow:auto; font-size:12px; line-height:1.5; }}
  pre.console {{ background:#111827; max-height:240px; }}
  .shot {{ max-width:100%; border:1px solid var(--c-line); border-radius:6px; margin-top:8px; }}
  a {{ color:var(--c-blue); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .keyword-box {{ background: #fdfefe; border: 1px solid var(--c-line); padding: 10px; border-radius: 6px; margin-top: 6px; }}
</style>
</head>
<body>
<div class="container">
  <h1>Reporte de pruebas · Farmatodo QA · wordcounter.net</h1>
  <div class="meta">
    Run ID <b>{self.run_id}</b> ·
    Inicio <b>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</b> ·
    Duración total <b>{total_duration}s</b>
  </div>

  <div class="kpis">
    <div class="kpi"><div class="v">{total}</div><div class="l">Total</div></div>
    <div class="kpi pass"><div class="v">{passed}</div><div class="l">Passed</div></div>
    <div class="kpi fail"><div class="v">{failed}</div><div class="l">Failed</div></div>
    <div class="kpi err"><div class="v">{error_count}</div><div class="l">Error</div></div>
    <div class="kpi skip"><div class="v">0</div><div class="l">Skipped</div></div>
    <div class="kpi"><div class="v">{efectividad}%</div><div class="l">Efectividad</div></div>
  </div>

  <h2>Índice de escenarios</h2>
  <table>
    <thead><tr><th>ID</th><th>Escenario</th><th>Estado</th><th>Duración</th><th>Error</th></tr></thead>
    <tbody>
      {index_rows_html}
    </tbody>
  </table>

  <h2>Detalle por escenario</h2>
  {details_html}
</div>
</body>
</html>
"""

        report_filename = f"test_report_{self.run_id}.html"
        report_path = os.path.join(self.output_dir, report_filename)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"\n[Reporte Generado] -> {report_path}")
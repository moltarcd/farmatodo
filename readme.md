# Prueba Técnica QA — Farmatodo

## 📋 Contexto

Este repositorio contiene las soluciones desarrolladas para los problemas planteados en la prueba técnica.

- **Ejercicio 1:** Suite de Pruebas Automatizadas con Python y Playwright (`wordcounter.net`).
- **Ejercicio 2:** Reporte de Fallas / Oportunidades de Mejora.
- **Ejercicio 3:** Reporte de Problemas de Experiencia de Usuario (UX) en la plataforma web y móvil.
- **Ejercicio 4:** Algoritmo de Conteo y Frecuencia de Palabras (Contador e Histograma).

## 📄 Reportes Documentados (Ejercicios 2 y 3)

La resolucion de los ejercicios 2 y 3  correspondientes al reporte de fallas y al análisis de experiencia de usuario (UX) se encuentran adjuntos en formato pdf dentro de la carpeta del proyecto:

- `exercises/Ejercicio_2_Reporte_de_Fallas.docx`
- `exercises/Ejercicio_3_Reporte_UX.docx`

---

## 🚀 Primeros pasos

### 1. Crear un entorno virtual

Desde la raíz del proyecto, ejecutar:

```bash
python -m venv .venv
```

### 2. Activar el entorno virtual

**En Windows (PowerShell / CMD):**

```bash
.venv\Scripts\activate
```

**En macOS / Linux:**

```bash
source .venv/bin/activate
```

---

## 📦 Instalación de dependencias

Con el entorno virtual activado, instalar las librerias Playwright y pytest:

```bash
pip install -r requirements.txt
```

A continuación, instala los binarios de los navegadores web requeridos:

```bash
playwright install
```

---

## 🧪 Ejecución de Pruebas

### Ejercicio 1 — Suite de Pruebas Automatizadas (Playwright)

Para ejecutar la suite automatizada sobre [https://wordcounter.net/](https://wordcounter.net/) (que valida conteo de palabras, caracteres y densidad de palabras ), posicionarse en la raíz del proyecto y ejecutar:

```bash
python .\test_wordcounter.py   
```

Al finalizar, el script generará automáticamente una carpeta `reports/` con un reporte en formato HTML que incluye KPIs de efectividad, trazas, logs  y capturas de pantalla de evidencia para todos los escenarios.

### Ejercicio 4 — Contador de Frecuencia de Palabras

Para ejecutar el algoritmo personalizado de procesamiento de texto, conteo e histograma, ejecutar:

```bash
python wordcounter.py
```

---

## 📁 Estructura del proyecto

```
C:\proyectos\farmatodo\
│
├── test_wordcounter.py      <-- Logica principal de las 
├── test_scenarios.py        <-- Definición de casos de prueba (Positivos, Borde, Negativos)
├── test_data.py             <-- URLs, datos de entrada y funciones hash
├── report_generator.py      <-- Módulo centralizado de reportes HTML y artefactos
├── wordcounter.py           <-- Algoritmo de frecuencia de palabras (Ejercicio 4)
├── input.txt                <-- Archivo con palabras a contar por el script wordcounter.py
└── exercises\               <-- Carpeta con La resolucion de los ejercicios 2 y 3
└── reports\                 <-- Carpeta autogenerada con historiales, HTML y evidencias visuales
    └── artifacts_<timestamp>\
        ├── TC-001_...png    <-- Capturas de pantalla
        └── TC-001_trace.zip <-- Trazas detalladas de Playwright
```


---

## 🛠️ Tecnologías y Herramientas Utilizadas

- **Python** (Lenguaje de programación base)
- **Playwright (Sync API)** (Framework moderno de pruebas end-to-end y automatización web)
- **HTML5 / CSS3** (Diseño de reportes ejecutivos personalizados)
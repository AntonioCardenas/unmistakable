<div align="center">

# Unmistakable

**Deja de publicar AI slop.**<br>
Una skill de diseño para agentes de código que prohíbe los degradados morados, los brillos neón, las tarjetas de vidrio y los heros 50/50 que todo modelo genera por defecto, mantiene cada icono y gráfico en un mismo lenguaje visual, y lo demuestra con un escáner offline de 57 reglas.

[![CI](https://github.com/AntonioCardenas/unmistakable/actions/workflows/ci.yml/badge.svg)](https://github.com/AntonioCardenas/unmistakable/actions/workflows/ci.yml)
[![Licencia: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![57 reglas](https://img.shields.io/badge/esc%C3%A1ner-57%20reglas-ab343b)](references/commands-and-audit-rubric.md)
[![Python 3.8+ stdlib](https://img.shields.io/badge/runtime-Python%203.8%2B%20stdlib-151423)](scripts/detect_slop.py)

Funciona con **Claude Code**, **Cursor**, **Codex CLI**, **Gemini CLI**, **GitHub Copilot**, **Windsurf**, **OpenCode** y **Google Antigravity**.

*Leer en otros idiomas: [English](README.md), [Español](README.es.md).*

</div>

![Lámina de comparación dibujada a mano sobre papel milimetrado. Panel izquierdo, Default slop, 55 hallazgos: hero 50/50 con píldora, dos botones píldora y tres tarjetas con icono, tachados en rojo. Panel derecho, Unmistakable, 0 hallazgos: jerarquía tipográfica, corte técnico con cotas y tabla de especificaciones.](assets/before-after.png)

<sub>Ilustración de las dos páginas de <a href="evals/fixtures/">evals/fixtures/</a>: mismo producto y mismos datos, construidos como lo hace un agente por defecto y con esta skill. Los conteos son reales; ejecuta el escáner en ambas.</sub>

## Por qué existe

Pide una landing page a un agente sin dirección y obtendrás el promedio estadístico de su entrenamiento: fondo pizarra oscuro, acento índigo, texto en degradado morado a cian, una píldora "✨ Nuevo · Con IA", un botón que brilla, una tarjeta de vidrio flotando y "10K+ clientes felices" que nadie contó.

Unmistakable le da al agente reglas de criterio que puede seguir y un escáner con el que no puede discutir:

- **Dirección antes que píxeles:** cada ruta tiene un Modo de Visitante (`Persuade`, `Operate`, `Read`, `Experience`) y un Contrato de Dirección de seis bloques.
- **Un solo lenguaje gráfico:** iconos, marcadores, divisores, gráficos pequeños, ilustraciones y tarjetas sociales salen de un inventario de motivos en `DESIGN.md`, con un solo trazo, una sola familia de iconos y colores del tema. Nada que el sistema de diseño no pueda nombrar.
- **Profundidad plana y honesta:** bordes de `1px` y escalones de superficie en lugar de brillos, degradados, vidrio y sombras apiladas. Un único token de sombra neutra para lo que realmente flota.
- **Cero datos inventados:** nada de cifras de usuarios, valoraciones, testimonios o logos fabricados.
- **Pruebas, no adjetivos:** 57 reglas deterministas, 18 compuertas de lanzamiento, salida SARIF y una GitHub Action. Solo librería estándar de Python.
- **SEO y GEO integrados:** JSON-LD válido, párrafos que los motores de respuesta citan, un robots.txt que mantiene la búsqueda con IA y excluye el entrenamiento, y una guía honesta sobre `llms.txt`.

## Instalación

```bash
npx skills add AntonioCardenas/unmistakable
```

En Claude Code:

```text
/plugin marketplace add AntonioCardenas/unmistakable
/plugin install unmistakable@unmistakable
```

O clona directamente en la carpeta de skills de tu agente:

```bash
git clone https://github.com/AntonioCardenas/unmistakable ~/.claude/skills/unmistakable
```

Luego pide a tu agente: `/unmistakable build`, `/unmistakable deslop src/app/page.tsx`, `/unmistakable audit` o `/unmistakable seo`.

## Qué prohíbe

El catálogo completo, con correcciones y excepciones, está en [references/anti-patterns.md](references/anti-patterns.md).

| Señal de IA | Qué hacer en su lugar | Regla |
|---|---|---|
| Acento `indigo-500` / `violet-500` de Tailwind | Un acento derivado de los materiales reales del producto | `UNM-42` |
| Degradados morado a cian o rosa | Un campo de color sólido y comprometido | `UNM-07` |
| Degradados decorativos en fondos, botones y bordes | Tokens semánticos sólidos | `UNM-41` |
| Halos de neón y sombras de color | Borde de `1px` y relleno sólido; sombras neutras solo en capas flotantes | `UNM-06`, `UNM-43` |
| Sombras pesadas o apiladas en tarjetas en reposo | Bordes y escalones de superficie | `UNM-44` |
| Glassmorphism | Superficies opacas con una línea fina | `UNM-45` |
| Orbes difuminados y blobs tipo aurora | Imagen real o un campo de color | `UNM-46` |
| Animaciones en bucle que flotan o laten | Movimiento solo como respuesta a una acción o estado real | `UNM-47` |
| Píldora "eyebrow" sobre el titular | Empezar con el encabezado | `UNM-01` |
| "Con la confianza de 10,000+", "4.9★" | Cifras con fuente, o nada | `UNM-50` |
| Seis radios distintos y `z-index: 9999` | Tres tokens de radio y una escala de capas | `UNM-48`, `UNM-49` |
| Emojis como iconos y viñetas | Una familia de iconos SVG definida en `DESIGN.md` | `UNM-32` |
| `lucide` junto a `react-icons` y Font Awesome | Una sola familia de iconos | `UNM-56` |
| Iconos con varios grosores y tamaños, colores fijos | `--stroke-icon`, tres tamaños, `currentColor` | `UNM-54`, `UNM-55` |
| Ilustraciones de stock (unDraw, Storyset) | Ilustraciones hechas con tu propio inventario de motivos | `UNM-57` |

¿Tu marca es realmente morada? Mantenla. Cada regla se puede eximir por línea o por archivo con un motivo escrito.

## Escáner y GitHub Action

```bash
python3 scripts/detect_slop.py src/                      # informe legible con correcciones
python3 scripts/detect_slop.py src/ --fail-on P1         # falla solo con hallazgos P0/P1
python3 scripts/detect_slop.py src/ --sarif > out.sarif  # GitHub code scanning
python3 scripts/check_foundations.py .                   # 18 compuertas de lanzamiento
```

```yaml
- uses: AntonioCardenas/unmistakable@v1
  with:
    path: src
    fail-on: P1
```

## Comandos

| Categoría | Comandos |
|---|---|
| **Sistema y setup** | `init` · `system [ref]` (genera `DESIGN.md`, `tokens.css`, `design-system.html` y `brand-book-a4.pdf`) · `document` · `extract` |
| **Construcción y dirección** | `shape` · `build` · `deslop` · `graphics` · `typeset` · `layout` · `colorize` · `animate` · `bolder` · `quieter` · `distill` |
| **Evaluación** | `audit` (puntuación `0-24` en 6 dimensiones con severidad `P0-P3`) · `critique` |
| **Producción, SEO/GEO y entrega** | `harden` · `optimize` · `seo` · `foundations` (18 compuertas) · `polish` |

## Preguntas frecuentes

### ¿Qué es Unmistakable?
Unmistakable es una skill open-source (MIT) que enseña a los agentes de código a construir interfaces web con una dirección visual propia en lugar del aspecto genérico de IA. Incluye un escáner offline de 57 reglas, 18 compuertas de lanzamiento, generadores de sistemas de diseño y brand books A4, y patrones de SEO técnico y GEO.

### ¿Funciona con React, Next.js, Astro, Vue, Svelte, Angular y Tailwind?
Sí. Los tokens son CSS Custom Properties estándar y el escáner lee `.tsx`, `.jsx`, `.vue`, `.svelte`, `.astro`, `.html`, `.css` y `.scss`, incluidas las clases de Tailwind.

### ¿Requiere claves de API o conexión a internet?
No. Todos los scripts usan la librería estándar de Python 3.8+, corren offline y no envían telemetría.

### ¿`llms.txt` mejora el posicionamiento en ChatGPT o Google?
No hay evidencia de ello. Google ha dicho que no lo usa para Search. Lo que sí ayuda a ser citado es contenido renderizado en el servidor, párrafos que responden primero, estadísticas con fuente y datos estructurados válidos.

## Contribuir

¿Viste una señal de IA que el escáner no detecta? Abre un issue de [nuevo patrón](https://github.com/AntonioCardenas/unmistakable/issues/new?template=new-slop-pattern.yml). ¿Un falso positivo? Usa la plantilla de [falso positivo](https://github.com/AntonioCardenas/unmistakable/issues/new?template=false-positive.yml).

## Licencia

MIT. Consulta [LICENSE](LICENSE).

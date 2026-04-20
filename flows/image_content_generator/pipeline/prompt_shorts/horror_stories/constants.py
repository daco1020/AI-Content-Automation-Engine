# flake8: noqa: E501
AUDIO_PROMPT: str = """Narra esta historia de terror ficticia con una voz activa, intensa y urgente, como un sobreviviente relatando un encuentro aterrador con la adrenalina aún a flor de piel.

Estilo de actuación:
- Tono: Tenso y directo. Evita ser demasiado solemne; busca una energía de "alerta máxima".
- Ritmo: Dinámico y rápido. Las pausas deben ser breves, casi como si te faltara el aliento por el miedo. Acelera en los momentos de mayor peligro.
- Énfasis: Golpea con fuerza las palabras clave como "sombra", "grito", "sangre", "miedo", "oscuro", "atrás".
- Emoción: Transmite urgencia y pavor real. La voz debe sonar viva, no estática ni monótona.
- No agregues sonidos ni muletillas. Lee exactamente lo que aparece.

Texto a narrar:
{audio_text}"""

IDEA_PROMPT_URBAN_LEGEND: str = """# 👻 PROMPT MAESTRO — AGENTE DE IDEAS DE TERROR (LEYENDAS URBANAS)
**Objetivo:** Generar una idea creativa para un video CORTO de una leyenda urbana aterradora.

**Instrucciones:**
1. **hook (Gancho de terror):** Una frase de 10-15 palabras que instale una duda aterradora en la mente del espectador (ej: "¿Sabes por qué nunca debes mirar debajo de tu cama a las 3:33 AM?", "Hay alguien en tu habitación ahora mismo, y no es humano.").
2. **Protagonista:** Una persona común en una situación cotidiana que se vuelve siniestra.
3. El concepto debe centrarse en un encuentro con lo sobrenatural o una regla extraña que, al romperse, desata el terror.
"""

SCRIPT_PROMPT: str = """# 📝 PROMPT MAESTRO — AGENTE GUIONISTA DE TERROR (STORYTELLING - SHORTS)
**Objetivo:** Crear un guion dinámico de 10 a 12 micro-escenas con un enfoque cinematográfico de horror y suspenso.

**Estructura del Guion (MANDATORIO):**
1. **Acto 1: La Inquietud [Escenas 1-4]:** DEBES usar el campo "hook" para la Escena 1. Establece una atmósfera pesada y presenta la anomalía.
2. **Acto 2: El Acecho [Escenas 5-10]:** La tensión escala. El protagonista se da cuenta de que algo está mal. Eventos inexplicables y visuales perturbadores.
3. **Acto 3: El Encuentro/Giro Final [Escenas 11-final]:** Un clímax aterrador o un giro oscuro que sella el destino del protagonista. Deja un sentimiento de inquietud.

## 📜 REGLAS OBLIGATORIAS

### 🟢 NARRACIÓN Y RITMO
- **Gancho:** Uso mandatorio del texto de `hook` literal en la Escena 1.
- **Diálogo/Narración:** Frases cortas, sugerentes y cargadas de misterio. Máximo una por escena.
- **Secuencialidad:** Atmósfera → Tensión → Terror → Resolución Oscura.
- **Fluidez:** Ritmo tenso y cinematográfico.

### 🔵 REGLAS VISUALES
- **Protagonista:** Presencia consistente de un personaje principal identificable enfrentando el horror.
- **Relación Imagen-Texto:** El `image_prompt` debe capturar visualmente el pavor de la narración (sombras largas, ojos en la oscuridad, ambientes lúgubres, expresiones de terror).
- **Sincronía Narrativa:** Lo que se escucha debe verse. Si el audio dice "escuché un susurro detrás de la puerta", la imagen debe mostrar una puerta entreabierta en la oscuridad absoluta.
- **Estilo:** DEBES usar el campo `style` para generar imágenes con un estilo visual de terror oscuro. La descripción en el campo `style` DEBE ser: `"Gritty hand-drawn 2D horror animation style, thick wobbly black ink outlines, staring eyes with tiny pupils, doll-like red rosy cheeks, expressive and slightly grotesque character designs, murky desaturated background, folk-horror cartoon aesthetic."`.
- **Uso del Color:** Utiliza una paleta base oscura y turbia (verdes musgo, grises sucios, negros). Usa el rojo de forma icónica para destacar mejillas rosadas tipo muñeca o sangre, y el blanco brillante para los ojos que resaltan en la penumbra, manteniendo un contraste crudo y perturbador.

### 🔴 ESTRUCTURA Y SALIDA
- **Extensión:** Entre 12 y 16 escenas.
- **Cierre:** Termina con un susurro final o una imagen que deje una pregunta aterradora.

### 🟠 IDIOMAS (ESTRICTO)
- **image_prompt:** DEBES generar todos los campos de `image_prompt` en **INGLÉS**.
- **narration:** DEBES generar el campo `narration` en **ESPAÑOL LATINOAMERICANO**.
"""

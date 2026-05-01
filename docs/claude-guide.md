# Guía de Claude Pro para FinSight

Consejos específicos de Claude Code y Claude Pro para desarrollar este proyecto. No son consejos genéricos de IA — son mecánicas concretas de Claude que aplican directamente a las fases de FinSight.

---

## 1. Niveles de Effort por Fase

El comando `/effort` ajusta la profundidad de razonamiento antes de hacer una pregunta. Más effort = respuesta más lenta pero más precisa en problemas complejos.

```
/effort normal   → preguntas rápidas, boilerplate, sintaxis
/effort high     → la mayoría de tareas de código
/effort xhigh    → debugging complejo, diseño de grafos
/effort max      → sesiones de diseño arquitectónico de alto impacto
```

| Semana | Fase | Effort recomendado | Razón |
|--------|------|--------------------|-------|
| 1 | Foundation / setup | `high` | La mayoría es boilerplate, pero MCP tiene casos edge no obvios |
| 2 | LangGraph core agent | `xhigh` | Diseño del grafo, estado compartido y flujo condicional son críticos |
| 3 | Frontend Next.js | `high` | Stack estándar; solo cambia a `xhigh` si hay un bug extraño |
| 4 | QA / debugging | `xhigh` | Bugs de agente son contraintuitivos — el contexto importa |
| 5 | Deployment | `high` | Debugging de Render/Vercel es específico, no arquitectónico |
| 6 | Docs / portfolio | `normal` | Escritura y formato no requieren razonamiento profundo |

**Cuándo usar `max`**: Reserva `max` para sesiones de diseño de alto impacto — como cuando decidas agregar Supabase, PDF export, o rediseñar el grafo del agente en el post-MVP. En la práctica, `xhigh` cubre el 95% de FinSight.

**Tip**: El nivel de effort se resetea al final de cada sesión. Ponlo al principio de la sesión si sabes que será una sesión compleja.

---

## 2. Cuándo Usar `/compact`

`/compact` comprime el historial para liberar contexto. Lo que pierdes: los detalles exactos del código que Claude vio antes. Lo que ganas: espacio para continuar la sesión.

**Verifica el uso con `/context` antes de decidir.** Si supera el 60%, empieza a pensar en compact.

### Cuándo sí:
- Entre semanas/fases del roadmap.
- Cuando terminas una tarea y empiezas una nueva dentro de la misma sesión.
- Cuando la sesión lleva más de 2 horas y cambiaste de tema varias veces.

### Cuándo no:
- En medio de un debugging activo — perderás el stack trace y el contexto del error.
- Cuando acabas de leer varios archivos que Claude necesita recordar para la siguiente pregunta.

### Después de hacer compact:
Siempre reintroduce el contexto relevante en tu siguiente mensaje:
```
Estoy en la Semana 3 de FinSight. El backend ya funciona (LangGraph + MCP + FastAPI).
El endpoint POST /api/chat responde correctamente via curl.
Ahora voy a construir el frontend en Next.js 14.
```

---

## 3. Gestión de Sesiones de Chat

### Cuándo empezar una sesión nueva:
- Al iniciar una nueva semana del roadmap.
- Al cambiar de componente principal (backend → frontend, implementación → deployment).
- Cuando la sesión se siente "pesada" — Claude responde fuera de contexto o mezcla temas de antes.

### Anti-patrón a evitar:
No mezcles diseño + implementación en la misma sesión larga sin compact. "¿Cómo debería diseñar el nodo analyzer?" seguido de 200 líneas de código, seguido de "espera, cambia el diseño" genera confusión acumulada.

### Buen patrón:
**Una sesión = un objetivo concreto.** Antes de empezar a escribir código, declara el objetivo:
```
Esta sesión: implementar el nodo fetcher en backend/app/agent/nodes.py
que llame a los 4 herramientas MCP y agregue raw_data al estado.
```

---

## 4. Claude Code vs. claude.ai Chat

| Tarea | Herramienta |
|-------|-------------|
| Escribir y editar código | **Claude Code** (CLI) |
| Leer archivos del proyecto | **Claude Code** |
| Git, tests, terminal | **Claude Code** (usa `!` prefix) |
| Revisar screenshots de LangSmith | **claude.ai** (sube la imagen) |
| Discutir arquitectura con un diagrama | **claude.ai** (sube el Excalidraw/PNG) |
| Code review de un PR completo | **Claude Code** con `/ultrareview` |
| Pregunta conceptual sin contexto de código | **claude.ai** (más rápido, sin overhead) |

**¿Solo Claude Code?** Para el 90% del proyecto, sí. La excepción es cuando tienes algo visual — una traza de LangSmith con un comportamiento inesperado, un screenshot de bug de UI — que necesitas discutir. Ahí claude.ai (Pro) con carga de imagen es más efectivo.

---

## 5. El Prefijo `!` — Shell en el Contexto

Dentro de Claude Code, `! <comando>` ejecuta el comando en tu terminal y su output queda en el contexto de la conversación. Útil para no copiar/pegar manualmente:

```bash
# Incluir el output de un test fallido directamente
! pytest tests/test_mcp_tools.py::test_get_financials -v

# Ver logs del backend en Docker
! docker-compose logs backend --tail=50

# Verificar que el endpoint responde
! curl -s http://localhost:8000/health

# Incluir el historial git reciente
! git log --oneline -10

# Ver el estado del agente en LangSmith (si usas CLI)
! cat backend/app/agent/graph.py
```

Después del output, haz tu pregunta — Claude ya tiene el contexto sin que tengas que copiar nada.

---

## 6. Cómo Arreglar un Prompt Mal Redactado

**Escenario 1: Claude respondió bien pero en la dirección equivocada**
```
Ignora esa respuesta. Déjame reformular:
[prompt mejorado con más contexto]
```

**Escenario 2: Olvidaste incluir contexto importante**
```
Contexto que olvidé mencionar: el MCP Server corre como subprocess de FastAPI
via stdio, no como servicio HTTP separado.
Con eso en mente: [tu pregunta original]
```

**Escenario 3: Claude empezó a generar código que no querías**
Presiona `Esc` para interrumpir la respuesta antes de que termine. Luego reformula.

**Escenario 4: La sesión completa se descarriló**
```
/clear
```
Resetea el contexto completamente. Empieza con una introducción limpia:
```
Proyecto: FinSight (FastAPI + LangGraph + MCP + Next.js)
Objetivo de esta sesión: [objetivo específico]
Contexto relevante: [solo lo que importa ahora]
```

**Regla de oro**: Un prompt malo + insistir en la misma sesión = más confusión. Es más rápido hacer `/clear` y empezar fresco que intentar "corregir" una sesión que se descarriló.

---

## 7. CLAUDE.md — Instrucciones Persistentes del Proyecto

Crea `CLAUDE.md` en la raíz de `finsight/` **el día 1**. Claude Code lo lee automáticamente al iniciar cada sesión. Esto elimina la necesidad de reintroducir el stack y los comandos cada vez.

El template para este proyecto ya está en `docs/repository-structure.md`. Cópialo a la raíz como `CLAUDE.md`.

**Actualiza CLAUDE.md cuando:**
- Agregues un nuevo comando importante (e.g., un script de migración post-MVP)
- Cambies una convención del proyecto
- Descubras algo no-obvio sobre el setup que querrías recordar la próxima sesión

**No pongas en CLAUDE.md:**
- Decisiones arquitectónicas detalladas (eso va en `docs/decisions.md`)
- Estado del progreso actual (eso es contexto de sesión, no persistente)
- Cosas que Claude puede derivar leyendo el código

---

## 8. Sistema de Memoria de Claude Code

Claude Code tiene memoria persistente entre sesiones (separada de CLAUDE.md). Úsala para preferencias personales y decisiones no-obvias que no encajan en documentación técnica.

**Ejemplos útiles para FinSight:**
```
Recuerda: en este proyecto prefiero commits pequeños y frecuentes,
no commits grandes al final del día.

Recuerda: el tier gratuito de Render tiene cold starts de ~30-50 segundos
en la primera request. Esto es esperado, no es un bug.

Recuerda: cuando revises el output del agente, siempre prueba con
Apple (AAPL), Tesla (TSLA) y una empresa latinoamericana como MercadoLibre (MELI)
para verificar que los tres casos funcionan.
```

**No guardes en memoria** lo que ya está en CLAUDE.md. La memoria es para preferencias tuyas; CLAUDE.md es para instrucciones técnicas del proyecto.

---

## 9. Cuándo Usar `/grill-me`

La skill `/grill-me` hace una entrevista de diseño relentless. Es para **stress-test de nuevos diseños**, no para implementación.

**Úsala cuando:**
- Vayas a comenzar el post-MVP (agregar Supabase, PDF export, multi-empresa)
- Tengas dudas sobre un trade-off arquitectónico antes de escribir código
- Quieras validar una decisión de diseño importante

**Invocación recomendada al inicio del post-MVP:**
```
/grill-me Voy a agregar persistencia de historial de chat en FinSight usando Supabase.
Stack actual: FastAPI stateless + Next.js. El frontend ya envía messages[] completo en cada request.
Quiero evaluar si agregar Supabase (sesiones, historial persistente) vale la complejidad.
```

---

## 10. Cuándo Usar `/ultrareview`

`/ultrareview` lanza un code review multi-agente del branch actual. Es el momento ideal para un review externo antes de hacer el deploy final.

**Momento óptimo para FinSight**: Al final de la Semana 4, cuando el código core esté completo y todavía puedas incorporar feedback antes de deployar.

```
/ultrareview
```

Sin argumentos revisa el branch actual vs. main. Ejecuta desde la raíz del repo.

---

## 11. Proyectos de Claude.ai Pro

Los Proyectos de claude.ai Pro mantienen contexto entre conversaciones en el browser. Son distintos de Claude Code y útiles para sesiones de diseño de alto nivel.

**Para FinSight, considera crear un Proyecto de claude.ai con:**
- Este documento adjunto
- `docs/architecture.md`
- `docs/decisions.md` (cuando lo completes)

Esto te permite tener conversaciones de diseño de alto nivel en claude.ai sin perder el contexto de las decisiones tomadas.

**No reemplaza Claude Code** para tareas de implementación — Claude Code tiene acceso directo al filesystem.

---

## 12. Reglas de Oro para FinSight

1. **CLAUDE.md el día 1** — Claude lo lee automáticamente en cada sesión.
2. **Una sesión = un objetivo concreto** — decláralo al inicio.
3. **`/compact` entre fases**, nunca en mitad de un debugging activo.
4. **`xhigh` para semanas 2 y 4**, `high` para el resto, `max` solo para diseño post-MVP.
5. **`!` prefix** para incluir output de comandos directamente en el contexto.
6. **Pega el stack trace completo** — Claude encuentra bugs mejor con el error exacto que con una descripción.
7. **Si la sesión se descarriló**, usa `/clear` y empieza fresco — no insistas en corregirla.
8. **`/grill-me`** antes de empezar features post-MVP.
9. **`/ultrareview`** al final de la Semana 4 antes de deployar.
10. **Commits frecuentes** — el historial de Git es parte del portafolio.

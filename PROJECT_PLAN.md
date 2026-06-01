# MyFeedMemory LinkedIn API Integration Plan

> Este documento es el plan completo y detallado del proyecto.
> `.docs/project.md` es el índice y la visión del proyecto, mientras que `PROJECT_PLAN.md` contiene el detalle de ejecución.

## 1. Objective

Desarrollar en esta rama una conexión segura a la API de LinkedIn para extraer contenido de la cuenta personal del usuario y convertirlo en una base de conocimiento buscable.

## 2. Alcance inicial

- Autenticación OAuth 2.0 con LinkedIn
- Petición de permisos mínimos para leer posts, artículos y actividad relevante
- Descarga de contenido personal de LinkedIn
- Normalización de los datos en un formato interno común
- Almacenamiento local o en una base de datos ligera
- Endpoint de prueba o script CLI para validar la integración

## 3. Restricciones y dependencias

- LinkedIn API requiere una aplicación registrada en LinkedIn Developers.
- Necesita credenciales: `CLIENT_ID`, `CLIENT_SECRET` y un token OAuth de usuario.
- La API de LinkedIn tiene límites de uso y permisos estrictos.
- El repositorio actual no tiene código de integración; partimos de una estructura mínima.

## 4. Arquitectura propuesta

### 4.1 Componentes principales

1. `auth/` — manejo de OAuth 2.0 y refresco de tokens.
2. `linkedin/` — cliente de LinkedIn, wrappers y mapeadores de recursos.
3. `storage/` — persistencia de datos estructurados (JSON, SQLite, etc.).
4. `cli/` — comandos de desarrollo rápido para probar la extracción.
5. `tests/` — pruebas unitarias y de integración simulando llamadas.
6. `docs/` — documentación del flujo y configuración.

### 4.2 Flujo de datos

1. El usuario inicia autorización desde la aplicación local.
2. Se obtiene `authorization_code` y se intercambia por `access_token`.
3. El cliente LinkedIn consulta los endpoints de contenido.
4. Los datos se normalizan a una estructura interna.
5. Se guardan en el almacenamiento local o en un índice de búsqueda.
6. La UI/CLI consume los datos para visualización o búsqueda.

## 5. Estructura de carpetas propuesta

```
MyFeedMemory/
├── .claude/
├── auth/
│   ├── linkedinoauth.py
│   └── config.py
├── linkedin/
│   ├── client.py
│   ├── models.py
│   └── extractor.py
├── storage/
│   ├── sqlite_store.py
│   └── json_store.py
├── cli/
│   └── fetch_linkedin.py
├── tests/
│   ├── test_linkedin_client.py
│   └── test_oauth_flow.py
├── requirements.txt
├── README.md
└── PROJECT_PLAN.md
```

## 6. Diseño de la integración con LinkedIn

### 6.1 Módulo `auth/linkedinoauth.py`

- Genera la URL de autorización.
- Intercambia códigos por tokens.
- Refresca tokens cuando caduquen.
- Lee credenciales desde variables de entorno (`LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_REDIRECT_URI`).

### 6.2 Módulo `linkedin/client.py`

- Encapsula llamadas HTTP a la API de LinkedIn.
- Configura cabeceras con `Authorization: Bearer <token>`.
- Implementa métodos como:
  - `get_profile()`
  - `get_posts()`
  - `get_articles()`
  - `get_activity()`

### 6.3 Módulo `linkedin/extractor.py`

- Orquesta las llamadas del cliente y normaliza respuestas.
- Convierte las respuestas en objetos internos como `FeedItem`.
- Extrae campos clave: texto, fecha, tipo, URL, métricas.

### 6.4 Módulo `storage/`

- Permite guardar datos de forma reproducible.
- `json_store.py` para un prototipo rápido.
- `sqlite_store.py` para almacenamiento estructurado.
- Incluye métodos de carga y actualización.

## 7. Configuración y variables de entorno

Variables básicas:

- `LINKEDIN_CLIENT_ID`
- `LINKEDIN_CLIENT_SECRET`
- `LINKEDIN_REDIRECT_URI`
- `LINKEDIN_ACCESS_TOKEN` (opcionales para pruebas)
- `LINKEDIN_REFRESH_TOKEN`
- `LINKEDIN_API_BASE_URL` (opcional)

Se puede mantener un archivo `.env` en local no versionado.

## 8. Dependencias sugeridas

- `requests` o `httpx` para HTTP
- `python-dotenv` para cargar variables de entorno
- `pytest` para pruebas
- `uvicorn` ya instalado para un posible servidor de prueba

## 9. Fases del proyecto

### Fase 1 — Investigación y setup

- Registrar la aplicación en LinkedIn Developers.
- Confirmar alcance de permisos necesarios.
- Definir exactos endpoints de LinkedIn que vamos a consumir.
- Crear el esquema de carpetas.

### Fase 2 — Autenticación OAuth 2.0

- Implementar el flujo de autorización.
- Probar intercambio de código por token.
- Guardar y refrescar tokens localmente.

### Fase 3 — Cliente LinkedIn y extractor

- Construir el cliente HTTP.
- Implementar llamadas a los endpoints de contenido.
- Normalizar respuestas.

### Fase 4 — Persistencia y prueba

- Guardar datos en JSON/SQLite.
- Crear un script CLI para ejecutar la extracción.
- Añadir pruebas unitarias.

### Fase 5 — Iteración y mejora

- Añadir paginación y manejo de límites.
- Agregar cache o reintentos.
- Diseñar la base de búsqueda o indexación futura.

## 10. Primeros entregables inmediatos

1. `PROJECT_PLAN.md` (este documento).
2. `auth/linkedinoauth.py` con esqueleto OAuth.
3. `linkedin/client.py` con cliente base.
4. `cli/fetch_linkedin.py` para validar el flujo.
5. `tests/test_oauth_flow.py` y `tests/test_linkedin_client.py`.

---

## Siguiente paso

Si quieres, avanzo ahora con la creación de la estructura inicial de carpetas y los archivos base de `auth/`, `linkedin/` y `cli/` en esta rama.

## Sprint 1 — Tareas inmediatas

- [x] Crear la estructura de código bajo `src/myfeedmemory/`.
- [x] Añadir un runner raíz `run.py` para ejecutar el flujo de extracción.
- [x] Añadir un paquete Python instalable con `pyproject.toml`.
- [ ] Definir los scopes exactos de LinkedIn y los endpoints de extracción.
- [ ] Implementar y validar el flujo OAuth 2.0.
- [ ] Añadir pruebas unitarias para el cliente LinkedIn y el normalizador.

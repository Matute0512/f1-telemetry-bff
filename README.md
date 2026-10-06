# F1 Telemetry BFF

Backend for Frontend (BFF) para la comparación **Head-to-Head de telemetría y vueltas de Fórmula 1**.

El proyecto consume datos públicos de [OpenF1], los procesa, normaliza y sincroniza para ofrecer al frontend una API REST optimizada y orientada específicamente a las necesidades de visualización y comparación de dos pilotos.

---

## Objetivo

El objetivo principal del backend es abstraer al frontend de la complejidad de consumir y combinar múltiples recursos de telemetría.

El sistema permitirá seleccionar:

* una sesión de Fórmula 1;
* dos pilotos;
* vueltas específicas o relevantes;

y obtener datos normalizados para realizar una comparación Head-to-Head.

Los datos de telemetría considerados incluyen, entre otros:

* coordenadas `X`;
* coordenadas `Y`;
* distancia recorrida;
* velocidad;
* acelerador;
* freno;
* marcha;
* timestamp.

La responsabilidad del BFF será transformar los datos externos en un modelo consistente y conveniente para el frontend.

---

## Arquitectura

El proyecto utiliza **Clean Architecture**, aplicando principios SOLID para mantener separadas las responsabilidades.

La estructura principal está dividida en:

```text
Domain
    ↓
Application
    ↓
Infrastructure

Presentation
    ↓
Application
    ↓
Domain
```

### Domain

Contiene las reglas y modelos fundamentales del negocio.

No depende de FastAPI, OpenF1, HTTP, Redis ni ningún otro detalle tecnológico.

Incluye entidades como:

* `Driver`
* `Circuit`
* `Lap`
* `TelemetryPoint`

También contiene los puertos/interfaces que necesita el dominio para interactuar con sistemas externos.

### Application

Contiene los casos de uso de la aplicación.

Ejemplos:

* `GetSessionLapsUseCase`
* `CompareDriversLapsUseCase`

Esta capa coordina el flujo de datos y utiliza las interfaces definidas por Domain.

### Infrastructure

Contiene las implementaciones concretas de las interfaces.

Actualmente se contempla:

* cliente HTTP para OpenF1 mediante `httpx`;
* caché en memoria;
* futura integración con Redis;
* repositorios;
* mappers entre modelos externos y modelos internos.

### Presentation

Contiene la API HTTP desarrollada con FastAPI.

Incluye:

* routers;
* endpoints;
* DTOs;
* schemas Pydantic;
* validación;
* manejo de errores;
* dependencias de FastAPI.

---

## Tecnologías

* Python `3.12+`
* FastAPI
* Pydantic v2
* Uvicorn
* HTTPX
* Pytest
* Ruff
* uv
* Git / GitFlow
* OpenF1 API

---

## Requisitos

Antes de comenzar se debe disponer de:

* Python 3.12 o superior.
* `uv`.
* Git.

Verificar:

```bash
python --version
uv --version
git --version
```

---

## Instalación

Clonar el repositorio:

```bash
git clone <REPOSITORY_URL>
cd f1-telemetry-bff
```

Instalar las dependencias y sincronizar el entorno:

```bash
uv sync
```

Esto crea o actualiza el entorno virtual `.venv` y utiliza `uv.lock` para reproducir las versiones de las dependencias.

---

## Variables de entorno

Crear un archivo `.env` a partir del ejemplo:

```bash
cp .env.example .env
```

El archivo `.env` es local y no debe versionarse.

Las variables de entorno estarán centralizadas en:

```text
src/f1_telemetry_bff_bff/config/settings.py
```

---

## Ejecución

Durante desarrollo se recomienda ejecutar FastAPI mediante Uvicorn:

```bash
uv run uvicorn f1_telemetry_bff_bff.main:app --reload
```

La aplicación quedará disponible en:

```text
http://127.0.0.1:8000
```

La documentación interactiva de FastAPI estará disponible en:

```text
/docs
```

y la documentación OpenAPI alternativa en:

```text
/redoc
```

---

## Testing

Ejecutar todos los tests:

```bash
uv run pytest
```

Ejecutar únicamente tests unitarios:

```bash
uv run pytest tests/unit
```

Ejecutar únicamente tests de integración:

```bash
uv run pytest tests/integration
```

Ejecutar un test específico:

```bash
uv run pytest tests/unit/path/to/test_file.py
```

---

## Linting y formatting

Ruff se utiliza como herramienta principal para análisis estático y formatting.

Verificar errores:

```bash
uv run ruff check .
```

Corregir automáticamente errores compatibles:

```bash
uv run ruff check . --fix
```

Formatear el proyecto:

```bash
uv run ruff format .
```

Verificar el formatting sin modificar archivos:

```bash
uv run ruff format . --check
```

---

## Flujo de desarrollo

El proyecto utiliza una estrategia basada en GitFlow.

Ramas principales:

```text
main
develop
```

Las nuevas funcionalidades se desarrollan mediante ramas:

```text
feature/<nombre>
```

Ejemplo:

```bash
git switch develop
git switch -c feature/new-endpoint
```

Una vez terminado el trabajo:

```bash
git add .
git commit -m "feat: add new endpoint"

git switch develop
git merge --no-ff feature/new-endpoint

git branch -d feature/new-endpoint
```

---

## Convención de commits

Se recomienda utilizar Conventional Commits.

Ejemplos:

```text
feat: add session laps endpoint
fix: handle missing telemetry data
refactor: extract telemetry mapper
test: add lap comparison tests
docs: update architecture documentation
chore: update dependencies
```

---

## Principios de diseño

El proyecto sigue los siguientes principios:

### Single Responsibility Principle

Cada componente debe tener una responsabilidad bien definida.

### Open/Closed Principle

Los componentes deben poder extenderse sin modificar innecesariamente el código existente.

### Liskov Substitution Principle

Las implementaciones concretas deben poder sustituir correctamente a las abstracciones que implementan.

### Interface Segregation Principle

Las interfaces deben ser pequeñas y específicas.

### Dependency Inversion Principle

Las capas de alto nivel dependen de abstracciones y no de implementaciones concretas.

---

## Clean Architecture

Una regla fundamental del proyecto es que el código interno no depende de detalles externos.

Por ejemplo:

```text
Domain
  ↑
Application
  ↑
Presentation
```

y:

```text
Infrastructure
      ↓
implements
      ↓
Domain Ports
```

Esto permite reemplazar OpenF1, el sistema de caché o incluso FastAPI sin tener que modificar las reglas centrales del negocio.

---

## Futuras funcionalidades

El backend está diseñado para permitir incorporar progresivamente:

* consulta de sesiones;
* consulta de pilotos;
* consulta de circuitos;
* consulta de vueltas;
* descarga de telemetría;
* normalización de telemetría;
* sincronización espacial;
* comparación Head-to-Head;
* cálculo de diferencias de tiempo;
* cálculo de diferencias de velocidad;
* análisis de acelerador y freno;
* caché;
* Redis;
* procesamiento concurrente;
* optimización de requests hacia OpenF1.

---

## Estado del proyecto

El proyecto se encuentra actualmente en la fase de **Project Setup**.

Esta fase establece:

* estructura del proyecto;
* Clean Architecture;
* configuración de `uv`;
* FastAPI;
* Pydantic;
* HTTPX;
* Pytest;
* Ruff;
* GitFlow;
* documentación arquitectónica.

La lógica de negocio de comparación de telemetría será implementada en etapas posteriores.

---

## Licencia

Este proyecto se distribuye bajo licencia MIT.

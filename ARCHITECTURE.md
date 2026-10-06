# Architecture

## 1. Introducción

F1 Telemetry BFF utiliza una arquitectura basada en **Clean Architecture**, complementada con principios SOLID y separación explícita entre dominio, aplicación, infraestructura y presentación.

El objetivo principal es mantener la lógica de negocio independiente de los frameworks, proveedores externos y mecanismos de transporte.

La arquitectura debe permitir modificar:

* OpenF1;
* FastAPI;
* HTTPX;
* Redis;
* el sistema de caché;
* los mecanismos de persistencia;

sin tener que modificar las reglas centrales del dominio.

---

# 2. Capas

La aplicación está organizada en cuatro áreas principales:

```text
┌──────────────────────────────────────────────┐
│                 Presentation                 │
│                  FastAPI                     │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                 Application                  │
│                 Use Cases                    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                   Domain                     │
│       Entities + Value Objects + Ports       │
└──────────────────────▲───────────────────────┘
                       │
                       │ implements
                       │
┌──────────────────────┴───────────────────────┐
│                Infrastructure                │
│        OpenF1 + Cache + Repositories         │
└──────────────────────────────────────────────┘
```

---

# 3. Domain

Domain es el núcleo de la aplicación.

Esta capa contiene conceptos relacionados directamente con el problema que estamos resolviendo.

Ejemplos:

```text
Driver
Circuit
Lap
TelemetryPoint
```

El Domain no conoce:

* FastAPI;
* HTTPX;
* OpenF1;
* Redis;
* JSON;
* HTTP;
* bases de datos.

Esto permite que el dominio pueda probarse sin levantar ningún servidor ni realizar requests HTTP.

---

## 3.1 Entidades

### Driver

Representa a un piloto.

Conceptualmente puede contener información como:

```text
Driver
├── driver_number
├── name
├── abbreviation
└── team
```

### Circuit

Representa un circuito.

```text
Circuit
├── circuit_key
├── name
├── location
└── country
```

### Lap

Representa una vuelta.

```text
Lap
├── driver
├── lap_number
├── lap_duration
├── date_start
└── telemetry
```

### TelemetryPoint

Representa un punto temporal de telemetría.

```text
TelemetryPoint
├── timestamp
├── x
├── y
├── distance
├── speed
├── throttle
├── brake
└── gear
```

---

# 4. Ports

El Domain define interfaces mediante puertos.

Por ejemplo:

```text
OpenF1Client
LapRepository
TelemetryRepository
```

La idea es definir **qué necesita la aplicación**, sin definir **cómo se obtiene**.

Ejemplo conceptual:

```text
Domain

OpenF1Client
    │
    │ interface
    ▼
Infrastructure

OpenF1HttpClient
```

La interfaz pertenece al núcleo.

La implementación pertenece a Infrastructure.

---

# 5. Application

Application contiene los casos de uso.

Esta capa representa acciones que el sistema puede realizar.

Ejemplos:

```text
GetSessionLapsUseCase
CompareDriversLapsUseCase
```

Los casos de uso no deberían conocer detalles de HTTP ni de FastAPI.

Por ejemplo:

```text
CompareDriversLapsUseCase
```

puede recibir:

```text
session
driver_a
driver_b
```

y utilizar los puertos necesarios para obtener y procesar los datos.

---

# 6. Infrastructure

Infrastructure contiene detalles técnicos.

Por ejemplo:

```text
infrastructure/
├── openf1/
│   ├── client.py
│   ├── schemas.py
│   └── mappers.py
│
├── cache/
│   ├── memory.py
│   └── redis.py
│
└── repositories/
```

---

## 6.1 OpenF1 Client

`OpenF1HttpClient` será la implementación concreta del puerto que requiere comunicación con OpenF1.

Utilizará `httpx`.

La dependencia queda de esta forma:

```text
Application
     │
     ▼
OpenF1Client
(interface)
     ▲
     │
     │ implements
     │
OpenF1HttpClient
     │
     ▼
OpenF1 API
```

Esto permite reemplazar el cliente real por un mock durante los tests.

---

# 7. Mappers

Los datos recibidos de OpenF1 no deberían propagarse directamente por todo el sistema.

Infrastructure será responsable de transformar los modelos externos en entidades del dominio.

Flujo:

```text
OpenF1 JSON
     │
     ▼
OpenF1 Schema
     │
     ▼
Mapper
     │
     ▼
Domain Entity
```

Por ejemplo:

```text
OpenF1TelemetryResponse
          │
          ▼
TelemetryMapper
          │
          ▼
TelemetryPoint
```

Esto evita acoplar el Domain al formato de OpenF1.

---

# 8. Presentation

Presentation contiene la API HTTP.

La estructura será:

```text
presentation/
└── api/
    ├── router.py
    │
    ├── routes/
    │   ├── sessions.py
    │   ├── laps.py
    │   └── comparison.py
    │
    └── schemas/
        ├── requests.py
        └── responses.py
```

Los schemas de Pydantic representan el contrato HTTP.

---

# 9. DTOs

Los DTOs de Presentation no deben confundirse con las entidades del Domain.

Por ejemplo:

```text
HTTP Request
     │
     ▼
Pydantic Request DTO
     │
     ▼
Application
     │
     ▼
Domain
```

Y para la respuesta:

```text
Domain
   │
   ▼
Application Result
   │
   ▼
Response DTO
   │
   ▼
HTTP Response
```

Esto permite mantener separados:

```text
API Contract
```

de:

```text
Business Model
```

---

# 10. Dependency Inversion

Uno de los principios más importantes será Dependency Inversion.

La aplicación no hará esto:

```python
use_case = CompareDriversLapsUseCase(OpenF1HttpClient())
```

porque eso acoplaría directamente el caso de uso a Infrastructure.

En cambio:

```text
CompareDriversLapsUseCase
        │
        ▼
   OpenF1Client
   <<interface>>
        ▲
        │
OpenF1HttpClient
```

El Use Case conoce solamente la abstracción.

FastAPI será responsable de ensamblar las implementaciones concretas.

---

# 11. Dependency Injection

El punto de composición estará principalmente en Presentation.

Conceptualmente:

```text
FastAPI
   │
   ├── OpenF1HttpClient
   ├── Cache
   └── Use Cases
          │
          ▼
       Endpoint
```

FastAPI puede utilizar dependency injection para proporcionar las dependencias necesarias a los routers.

Esto facilita:

* testing;
* reemplazo de implementaciones;
* configuración;
* mocking.

---

# 12. Flujo de una petición

Supongamos una futura petición:

```http
GET /api/v1/comparisons/{session_key}
```

solicitando la comparación entre dos pilotos.

El flujo será:

```text
Frontend
   │
   │ HTTP
   ▼
FastAPI Router
   │
   │ valida request
   ▼
Request DTO
   │
   ▼
Use Case
   │
   ├───────────────┐
   │               │
   ▼               ▼
OpenF1 Port     Cache Port
   │               │
   ▼               ▼
OpenF1 Client    Cache
   │
   ▼
OpenF1 API
```

Los datos vuelven:

```text
OpenF1 API
   │
   ▼
HTTP Response
   │
   ▼
OpenF1 Schema
   │
   ▼
Mapper
   │
   ▼
Domain Entity
   │
   ▼
Use Case
   │
   ▼
Comparison Result
   │
   ▼
Response DTO
   │
   ▼
FastAPI
   │
   ▼
Frontend
```

---

# 13. Principios SOLID

## Single Responsibility Principle

Cada clase debe tener una responsabilidad concreta.

Ejemplo:

```text
OpenF1HttpClient
```

se ocupa de comunicación HTTP con OpenF1.

No debe realizar comparación de vueltas.

Mientras:

```text
CompareDriversLapsUseCase
```

se ocupa del caso de uso de comparación.

No debe gestionar conexiones HTTP.

---

## Open/Closed Principle

Los componentes deben estar abiertos a extensión pero cerrados a modificación.

Por ejemplo, podemos comenzar con:

```text
InMemoryCache
```

y posteriormente agregar:

```text
RedisCache
```

sin modificar los casos de uso.

---

## Liskov Substitution Principle

Una implementación concreta debe poder reemplazar a su abstracción.

Por ejemplo:

```text
OpenF1Client
    ▲
    │
    ├── OpenF1HttpClient
    └── MockOpenF1Client
```

El Use Case debe poder trabajar con cualquiera de ellas.

---

## Interface Segregation Principle

Se evitarán interfaces gigantes.

En lugar de:

```text
ExternalDataRepository
```

con decenas de métodos, se utilizarán interfaces específicas:

```text
LapRepository
TelemetryRepository
```

cuando las responsabilidades lo justifiquen.

---

## Dependency Inversion Principle

Las capas de alto nivel dependerán de abstracciones.

```text
Use Case
   │
   ▼
Interface
   ▲
   │
Implementation
```

No:

```text
Use Case
   │
   ▼
Concrete HTTP Client
```

---

# 14. Regla de dependencias

Las dependencias deben apuntar hacia el interior.

```text
Presentation
     │
     ▼
Application
     │
     ▼
Domain
```

Infrastructure puede depender de Domain para implementar sus puertos:

```text
Infrastructure
      │
      ▼
Domain
```

Pero Domain nunca puede depender de Infrastructure.

Por ejemplo, esto estaría prohibido conceptualmente:

```text
domain/entities/lap.py
        │
        └── import httpx
```

Una entidad de dominio no debe saber que existe HTTPX.

---

# 15. OpenF1 como detalle externo

OpenF1 es considerado un proveedor externo.

Por lo tanto:

```text
OpenF1
```

no forma parte del Domain.

La arquitectura debe tratarlo como un detalle reemplazable.

```text
                ┌─────────────────┐
                │     Domain      │
                │                 │
                │ OpenF1Client    │
                │    <<port>>     │
                └────────▲────────┘
                         │
                         │ implements
                         │
                ┌────────┴────────┐
                │  Infrastructure │
                │                 │
                │ OpenF1HttpClient│
                └────────┬────────┘
                         │
                         ▼
                    OpenF1 API
```

Esto será particularmente útil para testing.

---

# 16. Cache

La caché también será abstraída.

Inicialmente puede utilizarse:

```text
InMemoryCache
```

para desarrollo y pruebas.

Posteriormente:

```text
RedisCache
```

para un entorno de producción.

El Use Case no debería conocer cuál se está utilizando.

```text
          CachePort
             ▲
             │
      ┌──────┴───────┐
      │              │
InMemoryCache    RedisCache
```

---

# 17. Testing

Los tests estarán divididos en:

```text
tests/
├── unit/
│   ├── domain/
│   ├── application/
│   └── infrastructure/
│
└── integration/
    ├── api/
    └── infrastructure/
```

## Unit tests

No deberían depender de servicios externos.

Ejemplos:

```text
test_lap.py
test_telemetry_point.py
test_compare_drivers_laps.py
```

Los clientes externos serán reemplazados por mocks o fakes.

---

## Integration tests

Verifican que varios componentes funcionen correctamente juntos.

Por ejemplo:

```text
FastAPI
   +
Dependency Injection
   +
Use Case
   +
Fake OpenF1 Client
```

No necesariamente deben depender de la API real.

Los tests contra servicios externos reales deberían mantenerse separados debido a su costo, latencia y potencial inestabilidad.

---

# 18. Performance

El backend está diseñado considerando que OpenF1 puede requerir múltiples requests para construir una respuesta completa.

Por este motivo se contemplan desde el diseño:

* HTTP asíncrono mediante `httpx.AsyncClient`;
* concurrencia controlada;
* reutilización de conexiones HTTP;
* caché;
* reducción de requests duplicadas;
* normalización en backend;
* respuestas específicas para el frontend;
* procesamiento eficiente de telemetría.

La optimización prematura de la lógica de comparación se evitará durante la primera etapa.

Primero se establecerá una arquitectura correcta y medible.

---

# 19. Futuro flujo de Head-to-Head

La funcionalidad principal tendrá conceptualmente este flujo:

```text
Session
   │
   ├──────────────┐
   │              │
Driver A       Driver B
   │              │
   ▼              ▼
Laps A          Laps B
   │              │
   ▼              ▼
Telemetry A    Telemetry B
   │              │
   └──────┬───────┘
          ▼
    Normalization
          │
          ▼
     Synchronization
          │
          ▼
   Head-to-Head Model
          │
          ▼
      REST API
          │
          ▼
       Frontend
```

La responsabilidad de cada etapa será mantenida separada para evitar crear un único servicio monolítico que realice todas las operaciones.

---

# 20. Objetivo arquitectónico

La arquitectura debe permitir que el siguiente código conceptual sea posible:

```text
Frontend
    ↓
FastAPI
    ↓
CompareDriversLapsUseCase
    ↓
Domain
    ↓
OpenF1Client interface
    ↓
OpenF1HttpClient
    ↓
OpenF1
```

pero también:

```text
Test
    ↓
CompareDriversLapsUseCase
    ↓
FakeOpenF1Client
```

sin modificar el Use Case.

Ese es uno de los principales objetivos de utilizar Clean Architecture en este proyecto.

# Panel administrativo

## Estado actual

Los Bloques 6B y 6C establecen la base tecnica y visual del panel administrativo
de Agente Activa e implementan el primer modulo funcional: clientes. Los modulos
de productos y pedidos todavia son rutas preparadas sin flujos completos.

Incluye:

- Next.js con App Router y TypeScript.
- Navegacion responsive para resumen, clientes, productos, pedidos y health.
- Rutas preparadas para los modulos administrativos.
- Cliente HTTP centralizado para FastAPI.
- Consulta real del endpoint `/api/v1/health`.
- Manejo visual de disponibilidad y errores de API.
- Busqueda explicita de clientes sin llamadas por cada tecla.
- Registro seguro de clientes mediante Server Actions.
- Deteccion y presentacion de posibles duplicados.
- Vista de detalle de cliente.
- Asociacion de telefonos, alias y direcciones.

## Requisitos locales

- Node.js y npm instalados en Windows.
- Backend disponible en `http://localhost:8000`.

## Configuracion

La variable `API_BASE_URL` se usa exclusivamente del lado servidor:

```text
API_BASE_URL=http://localhost:8000
```

El ejemplo se encuentra en `apps/admin/.env.example`. No se usa
`NEXT_PUBLIC_API_BASE_URL`, porque el navegador no debe comunicarse directamente
con FastAPI en este bloque.

Si en el futuro Next.js se ejecuta dentro de un contenedor, podria requerirse:

```text
API_BASE_URL=http://host.docker.internal:8000
```

## Arquitectura de comunicacion

```text
Navegador
  -> Next.js App Router
    -> Server Component
      -> cliente HTTP centralizado
        -> FastAPI
```

La consulta de health se ejecuta en el servidor de Next.js. El boton Actualizar
solicita una nueva renderizacion del Server Component y no llama FastAPI desde
el navegador. Por esta razon, el Bloque 6B no necesita modificar CORS.

Archivos principales:

- `src/lib/config.ts`: configuracion privada de `API_BASE_URL`.
- `src/lib/api/http.ts`: cliente HTTP centralizado y server-only.
- `src/lib/api/errors.ts`: interpretacion del contrato uniforme de errores.
- `src/lib/api/health.ts`: acceso tipado al healthcheck.
- `src/app/health/page.tsx`: vista server-side del estado de la API.
- `src/lib/api/customers.ts`: acceso centralizado a endpoints de clientes.
- `src/lib/api/customer-types.ts`: contratos TypeScript del modulo.
- `src/app/customers/actions.ts`: mutaciones server-side.
- `src/app/customers/page.tsx`: busqueda, creacion y deteccion de duplicados.
- `src/app/customers/[customerId]/page.tsx`: detalle y asociacion de datos.

## Modulo de clientes

La busqueda se ejecuta unicamente cuando el usuario envia el formulario. La
pagina usa sus query params para solicitar resultados desde un Server Component,
por lo que no hay polling, llamadas por tecla ni solicitudes directas del
navegador hacia FastAPI.

Las operaciones de creacion y asociacion de datos se ejecutan mediante Server
Actions. Estas acciones realizan validaciones basicas para experiencia de
usuario, pero FastAPI conserva la validacion y decision final.

Operaciones disponibles:

- Buscar por telefono, nombre, alias, direccion o referencia.
- Crear un cliente con nombre y datos asociados opcionales.
- Detectar posibles duplicados y mostrar razones, score y confianza.
- Consultar detalle, telefonos, alias y direcciones.
- Agregar telefonos, alias y direcciones a un cliente existente.
- Mostrar errores uniformes enviados por FastAPI.

## Ejecutar localmente

Primero levantar el backend desde la raiz:

```powershell
docker compose up -d --build
```

Luego iniciar el panel:

```powershell
cd apps/admin
npm run dev
```

Abrir `http://localhost:3000`.

## Validar

Desde `apps/admin`:

```powershell
npm run lint
npm run typecheck
npm run build
```

Desde la raiz del repositorio:

```powershell
docker compose exec api python -m pytest
docker compose exec api python -m ruff check app tests
Invoke-RestMethod http://localhost:8000/api/v1/health
```

## Limites actuales

- No implementa flujos visuales de productos o pedidos.
- No modifica el backend ni Docker Compose.
- No agrega autenticacion.
- No integra WhatsApp.
- No expone variables privadas al navegador.

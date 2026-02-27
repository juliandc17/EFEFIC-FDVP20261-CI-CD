
# EFEFIC-FDVP20261: API Gateway CI/CD 

Este repositorio contiene la implementación de un **API Gateway** desarrollado con **FastAPI**, diseñado para centralizar la comunicación de microservicios y gestionado bajo un ciclo de vida **DevOps** automatizado.

## Arquitectura del Ecosistema
El proyecto integra un flujo completo de CI/CD para garantizar la calidad y disponibilidad del software:

## Arquitectura CI/CD

1. **Integración Continua (CI):** Ejecutada en **GitHub Actions**. Realiza pruebas unitarias automáticas con `pytest` ante cada `push`.
2. **Entrega Continua (CD):** Orquestada por **Jenkins**. Se encarga del empaquetado Docker y el despliegue en un clúster de **Kubernetes**.
3. **Validación (Smoke Test):** Jenkins realiza una verificación de salud dinámica post-despliegue para confirmar la operatividad del servicio.

## Tecnologías Principales
- **Backend:** FastAPI (Python 3.11)
- **CI Server:** GitHub Actions
- **CD Server:** Jenkins (Pipeline as Code)
- **Containerization:** Docker & Docker Hub
- **Orchestration:** Kubernetes (Docker Desktop)

```
Developer → Push/PR → GitHub
                         │
              ┌──────────▼──────────┐
              │  GitHub Actions CI  │
              │  1. Lint (Black/    │
              │     Flake8/isort)   │
              │  2. Tests (pytest)  │
              │  3. Docker Build    │
              └──────────┬──────────┘
                         │ merge to main
              ┌──────────▼──────────┐
              │   Jenkins CD        │
              │  1. Checkout        │
              │  2. Docker Build    │
              │  3. Push DockerHub  │
              │  4. Deploy K8s      │
              │  5. Smoke Test      │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────────┐
              │  Kubernetes Cluster     │
              │  NS:efefic-fdvp20261-u2 │
              │  Deployment + SVC       │
              └─────────────────────────┘
```

---

## Estructura del Proyecto

```
EFEFIC-FDVP20261-CI-CD/
  .github/
    workflows/
      ci.yml                # Pipeline CI — GitHub Actions 
  app/
    __init__.py
    main.py                 # FastAPI — API Gateway proxy a microservicios
  tests/
    __init__.py
    test_main.py            # 4 pruebas unitarias con pytest
  k8s/
    deployment.yaml         # Deployment + Service LoadBalancer puerto 8081
    microservices-mock.yaml # Mocks auth, users, broadcast
  conftest.py               # Configuracion de path para pytest
  Dockerfile                # Imagen multistage Python 3.11-slim
  Jenkinsfile               # Pipeline CD con 5 stages declarativos
  requirements.txt          # Dependencias Python del proyecto
  README.md                 # Documentacion con evidencias y screenshots


```

---

## Pipeline CI — GitHub Actions

**Archivo:** `.github/workflows/ci.yml`

Se activa automáticamente con cada **push** o **pull request** a las ramas `main` y `develop`.

| Stage | Descripción | Herramienta |
|---|---|---|
| Lint | Análisis estático y formato de código | Black, Flake8, isort |
| Tests | Ejecución de pruebas unitarias | pytest |
| Docker Build | Validación de construcción de imagen | Docker Buildx |

---

## Pipeline CD — Jenkins

**Archivo:** `Jenkinsfile`

Se activa manualmente o mediante webhook al mergear en `main`.

| Stage | Descripción |
|---|---|
| Checkout | Clona el repositorio desde GitHub |
| Build | Construye la imagen Docker con tag `BUILD_NUMBER` y `latest` |
| Push | Publica la imagen en DockerHub |
| Deploy | Actualiza el Deployment en Kubernetes con `kubectl set image` |
| Smoke Test | Verifica el endpoint `/health` post-despliegue |

### Credenciales requeridas en Jenkins

| ID | Tipo | Descripción |
|---|---|---|
| `dockerhub-credentials` | Username/Password | Cuenta DockerHub |
| `kubeconfig-efefic-u2` | Secret File | kubeconfig del cluster K8s |

---



## 🌐 Endpoints del Gateway

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Health check del gateway |
| GET | `/` | Información del servicio |
| ANY | `/{service}/{path}` | Proxy a microservicio destino |

### Servicios disponibles

| Key | Variable de Entorno | Default |
|---|---|---|
| `auth` | `AUTH_SERVICE_URL` | `http://auth-service:8001` |
| `users` | `USERS_SERVICE_URL` | `http://users-service:8002` |
| `broadcast` | `BROADCAST_SERVICE_URL` | `http://broadcast-service:8003` |

---

## 🔗 Herramientas utilizadas

| Herramienta | Rol en el ciclo DevOps |
|---|---|
| **GitHub** | Control de versiones, trigger de pipelines |
| **GitHub Actions** | Integración Continua (CI) |
| **Jenkins** | Entrega Continua (CD) |
| **Docker** | Containerización de la aplicación |
| **DockerHub** | Registro de imágenes |
| **Kubernetes** | Orquestación y despliegue |
| **FastAPI** | Framework del API Gateway |
| **pytest** | Testing unitario |
| **Black/Flake8** | Calidad y estilo de código |
# test trigger


## Evidencias de Despliegue

### 1. Integración Continua (GitHub Actions)
Muestra la validación automática del código y los tests pasando en la nube.
![CI Pipeline](images/Evidencia-u2%20lab%20CI.png)

### 2. Orquestación y Despliegue (Kubernetes)
Evidencia de los Pods y Servicios (Auth, Users, Broadcast) corriendo correctamente.
![K8s Resources](images/Evidencia-u2%20lab%20k8s.png)

### 3. Entrega Continua (Jenkins)
Vista del Stage View con todas las etapas en verde, incluyendo el Smoke Test.
![Jenkins CD](images/Evidencia-u2%20lab%20CD.png)
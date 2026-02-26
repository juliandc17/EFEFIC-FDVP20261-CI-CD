# API Gateway

API Gateway centralizado para los microservicios de la plataforma **Broadcom**, construido con **FastAPI** y desplegado en contenedores Docker sobre un cluster **Kubernetes**.

---

## 📐 Arquitectura CI/CD

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
              ┌──────────▼──────────┐
              │  Kubernetes Cluster │
              │  Namespace:broadcmo │
              │  Deployment + SVC   │
              └─────────────────────┘
```

---

## 🗂️ Estructura del Proyecto

```
broadcmo-api-gateway/
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline CI - GitHub Actions
├── app/
│   └── main.py                 # Aplicación FastAPI
├── tests/
│   └── test_main.py            # Pruebas unitarias
├── Dockerfile                  # Imagen del contenedor
├── Jenkinsfile                 # Pipeline CD - Jenkins
├── requirements.txt            # Dependencias Python
└── README.md
```

---

## ⚙️ Pipeline CI — GitHub Actions

**Archivo:** `.github/workflows/ci.yml`

Se activa automáticamente con cada **push** o **pull request** a las ramas `main` y `develop`.

| Stage | Descripción | Herramienta |
|---|---|---|
| 🔍 Lint | Análisis estático y formato de código | Black, Flake8, isort |
| 🧪 Tests | Ejecución de pruebas unitarias | pytest |
| 🐳 Docker Build | Validación de construcción de imagen | Docker Buildx |

---

## 🔧 Pipeline CD — Jenkins

**Archivo:** `Jenkinsfile`

Se activa manualmente o mediante webhook al mergear en `main`.

| Stage | Descripción |
|---|---|
| 📥 Checkout | Clona el repositorio desde GitHub |
| 🐳 Build | Construye la imagen Docker con tag `BUILD_NUMBER` y `latest` |
| 📤 Push | Publica la imagen en DockerHub |
| 🚀 Deploy | Actualiza el Deployment en Kubernetes con `kubectl set image` |
| 🔎 Smoke Test | Verifica el endpoint `/health` post-despliegue |

### Credenciales requeridas en Jenkins

| ID | Tipo | Descripción |
|---|---|---|
| `dockerhub-credentials` | Username/Password | Cuenta DockerHub |
| `kubeconfig-broadcmo` | Secret File | kubeconfig del cluster K8s |

---

## 🐳 Docker

### Build local

```bash
docker build -t broadcmo-api-gateway:local .
```

### Run local

```bash
docker run -p 8000:8000 \
  -e AUTH_SERVICE_URL=http://localhost:8001 \
  broadcmo-api-gateway:local
```

---

## 🧪 Pruebas locales

```bash
pip install -r requirements.txt
pytest tests/ -v
```

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

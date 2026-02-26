pipeline {
    agent any

    environment {
        // ── Configuración del proyecto ──────────────────────────
        APP_NAME        = 'broadcmo-api-gateway'
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE    = "${DOCKER_REGISTRY}/${DOCKER_HUB_USER}/${APP_NAME}"
        K8S_NAMESPACE   = 'broadcmo'

        // ── Credenciales (configuradas en Jenkins Credentials) ──
        DOCKER_CREDENTIALS = credentials('dockerhub-credentials')
        KUBECONFIG_FILE    = credentials('kubeconfig-broadcmo')
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {

        // ────────────────────────────────────────────────────────
        // STAGE 1: Clonar repositorio
        // ────────────────────────────────────────────────────────
        stage('📥 Checkout') {
            steps {
                echo "==> Clonando repositorio: ${APP_NAME}"
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        // ────────────────────────────────────────────────────────
        // STAGE 2: Construir imagen Docker
        // ────────────────────────────────────────────────────────
        stage('🐳 Build Docker Image') {
            steps {
                echo "==> Construyendo imagen Docker para ${APP_NAME}:${BUILD_NUMBER}"
                sh """
                    docker build \
                        --tag ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                        --tag ${DOCKER_IMAGE}:latest \
                        --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                        --build-arg GIT_COMMIT=\$(git rev-parse --short HEAD) \
                        .
                """
                echo "✅ Imagen construida: ${DOCKER_IMAGE}:${BUILD_NUMBER}"
            }
        }

        // ────────────────────────────────────────────────────────
        // STAGE 3: Publicar imagen en DockerHub
        // ────────────────────────────────────────────────────────
        stage('📤 Push to DockerHub') {
            steps {
                echo "==> Publicando imagen en DockerHub"
                sh """
                    echo \${DOCKER_CREDENTIALS_PSW} | \
                        docker login ${DOCKER_REGISTRY} \
                        -u \${DOCKER_CREDENTIALS_USR} \
                        --password-stdin

                    docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                    docker push ${DOCKER_IMAGE}:latest
                """
                echo "✅ Imagen publicada: ${DOCKER_IMAGE}:${BUILD_NUMBER}"
            }
        }

        // ────────────────────────────────────────────────────────
        // STAGE 4: Despliegue en Kubernetes
        // ────────────────────────────────────────────────────────
        stage('🚀 Deploy to Kubernetes') {
            steps {
                echo "==> Desplegando en cluster Kubernetes (namespace: ${K8S_NAMESPACE})"
                withCredentials([file(credentialsId: 'kubeconfig-broadcmo', variable: 'KUBECONFIG')]) {
                    sh """
                        kubectl set image deployment/${APP_NAME} \
                            ${APP_NAME}=${DOCKER_IMAGE}:${BUILD_NUMBER} \
                            -n ${K8S_NAMESPACE}

                        kubectl rollout status deployment/${APP_NAME} \
                            -n ${K8S_NAMESPACE} \
                            --timeout=120s
                    """
                }
                echo "✅ Despliegue completado en Kubernetes"
            }
        }

        // ────────────────────────────────────────────────────────
        // STAGE 5: Verificación post-despliegue (Smoke Test)
        // ────────────────────────────────────────────────────────
        stage('🔎 Smoke Test') {
            steps {
                echo "==> Ejecutando prueba de humo post-despliegue"
                withCredentials([file(credentialsId: 'kubeconfig-broadcmo', variable: 'KUBECONFIG')]) {
                    sh """
                        GATEWAY_URL=\$(kubectl get svc ${APP_NAME} \
                            -n ${K8S_NAMESPACE} \
                            -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

                        curl -sf http://\${GATEWAY_URL}/health | grep '"status":"healthy"'
                        echo "✅ Smoke test exitoso"
                    """
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Pipeline CD completado exitosamente — Build #${BUILD_NUMBER}"
        }
        failure {
            echo "❌ Pipeline CD falló en Build #${BUILD_NUMBER} — revisar logs"
        }
        always {
            // Limpiar imágenes locales para ahorrar espacio en el agente
            sh "docker rmi ${DOCKER_IMAGE}:${BUILD_NUMBER} || true"
            sh "docker rmi ${DOCKER_IMAGE}:latest || true"
        }
    }
}

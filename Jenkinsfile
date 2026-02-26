pipeline {
    agent any

    environment {
        // ── Configuración del proyecto (valores fijos, no son secretos) ──
        APP_NAME        = 'efefic-u2-api-gateway'
        DOCKER_REGISTRY = 'docker.io'
        K8S_NAMESPACE   = 'efefic-fdvp20261-u2'

        // ── Secretos — definidos en Jenkins Credentials Manager ──
        // Configurar en: Manage Jenkins > Credentials > Global
        //   ID: dockerhub-credentials  → Username/Password (usuario y pass de DockerHub)
        //   ID: kubeconfig-efefic      → Secret file (kubeconfig del cluster K8s)
        DOCKER_CREDENTIALS = credentials('dockerhub-credentials')
        KUBECONFIG_FILE    = credentials('kubeconfig-efefic-u2')
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
        stage('Checkout') {
            steps {
                echo "==> Clonando repositorio: ${APP_NAME}"
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        // ────────────────────────────────────────────────────────
        // STAGE 2: Construir imagen Docker
        // ────────────────────────────────────────────────────────
        stage('Build Docker Image') {
            steps {
                echo "==> Construyendo imagen Docker para ${APP_NAME}:${BUILD_NUMBER}"
                sh "docker build --tag ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${APP_NAME}:${BUILD_NUMBER} ."
                echo "==> Imagen construida correctamente"
            }
        }

        // ────────────────────────────────────────────────────────
        // STAGE 3: Publicar imagen en DockerHub
        // ────────────────────────────────────────────────────────
        stage('Push to DockerHub') {
            steps {
                echo "==> Publicando imagen en DockerHub"
                sh 'echo $DOCKER_CREDENTIALS_PSW | docker login docker.io -u $DOCKER_CREDENTIALS_USR --password-stdin'
                sh "docker push ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${APP_NAME}:${BUILD_NUMBER}"
                sh "docker tag ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${APP_NAME}:${BUILD_NUMBER} ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${APP_NAME}:latest"
                sh "docker push ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${APP_NAME}:latest"
                echo "==> Imagen publicada correctamente"
            }
        }

        // ────────────────────────────────────────────────────────
        // STAGE 4: Despliegue en Kubernetes
        // ────────────────────────────────────────────────────────
       stage('Deploy to Kubernetes') {
            steps {
                echo "==> Verificando archivos en el workspace:"
                sh "ls -la" // Esto nos dirá si el archivo está ahí realmente
                
                echo "==> Aplicando configuración en ${K8S_NAMESPACE}"
                withCredentials([file(credentialsId: 'kubeconfig-efefic-u2', variable: 'KUBECONFIG')]) {
                    // Asegúrate de que el nombre del archivo abajo sea EXACTAMENTE el mismo que en tu repo
                    sh "kubectl apply -f k8s/deployment.yaml -n ${K8S_NAMESPACE}"
                    
                    sh "kubectl set image deployment/${APP_NAME} ${APP_NAME}=${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${APP_NAME}:${BUILD_NUMBER} -n ${K8S_NAMESPACE}"
                    sh "kubectl rollout status deployment/${APP_NAME} -n ${K8S_NAMESPACE} --timeout=120s"
                }
            }
        }

        // ────────────────────────────────────────────────────────
        // STAGE 5: Verificación post-despliegue (Smoke Test)
        // ────────────────────────────────────────────────────────
        stage('Smoke Test') {
            steps {
                echo "==> Ejecutando prueba de humo en entorno local (Docker Desktop)"
                withCredentials([file(credentialsId: 'kubeconfig-efefic-u2', variable: 'KUBECONFIG')]) {
                    sh """
                        # 1. Intentamos obtener la IP del LoadBalancer (en Docker Desktop suele ser localhost o vacio)
                        GATEWAY_URL=\$(kubectl get svc ${APP_NAME} -n ${K8S_NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
                        
                        # 2. Si está vacío (típico de local), usamos localhost
                        if [ -z "\$GATEWAY_URL" ]; then
                            echo "Info: Usando localhost para el test local."
                            GATEWAY_URL="localhost"
                        fi

                        echo "Probando conexión en: http://\$GATEWAY_URL/health"
                        
                        # 3. Reintentos: La app ya debería estar READY por el 'rollout status' anterior,
                        # pero damos unos segundos por si acaso.
                        SUCCESS=0
                        for i in {1..5}; do
                            # IMPORTANTE: Usamos puerto 80 porque es el 'port' definido en el Service
                            if curl -sf http://\$GATEWAY_URL/health | grep "healthy"; then
                                echo "--------------------------------------------------"
                                echo "==> ¡SMOKE TEST EXITOSO!"
                                echo "La API Gateway respondió correctamente."
                                echo "--------------------------------------------------"
                                SUCCESS=1
                                break
                            fi
                            echo "Intento \$i: La app aún no responde en http://\$GATEWAY_URL/health, reintentando..."
                            sleep 5
                        done

                        if [ \$SUCCESS -eq 0 ]; then
                            echo "ERROR: El Smoke Test falló tras varios intentos."
                            exit 1
                        fi
                    """
                }
            }
        }
    }

    post {
        success {
            echo "==> Pipeline CD completado exitosamente - Build #${BUILD_NUMBER}"
        }
        failure {
            echo "==> Pipeline CD fallo en Build #${BUILD_NUMBER} - revisar logs"
        }
        always {
            sh "docker rmi ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${APP_NAME}:${BUILD_NUMBER} || true"
            sh "docker rmi ${DOCKER_REGISTRY}/${DOCKER_CREDENTIALS_USR}/${APP_NAME}:latest || true"
        }
    }
}
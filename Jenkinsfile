pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    # Créer un environnement virtuel Python
                    python -m venv venv
                    
                    # Activer le venv et installer les dépendances
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    # Activer le venv et lancer pytest
                    . venv/bin/activate
                    pytest tests/ -v --tb=short
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t inbox_debt .'
            }
        }

        stage('Run Container Test') {
            steps {
                sh 'docker run -d --name inbox_debt_test -p 8081:8080 -e APP_MODE=demo inbox_debt'
            }
        }

        stage('Health Check') {
            steps {
                sh 'sleep 5'
                sh 'curl -f http://localhost:8081'
            }
        }

        stage('Deploy Railway') {
            steps {
                sh '''
                    # Déployer vers Railway si configuré
                    echo "Déploiement vers Railway..."
                    # Remplacer par la véritable commande de déploiement Railroad
                    # railway up
                '''
            }
        }
    }

    post {
        always {
            sh 'docker stop inbox_debt_test || true'
            sh 'docker rm inbox_debt_test || true'
        }
    }
}
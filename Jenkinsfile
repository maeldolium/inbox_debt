pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
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
    }

    post {
        always {
            sh 'docker stop inbox_debt_test || true'
            sh 'docker rm inbox_debt_test || true'
        }
    }
}
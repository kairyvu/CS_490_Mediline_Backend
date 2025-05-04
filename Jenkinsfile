pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        script {
          checkout scm
        }
      }
    }

    stage('Build & Test in Docker') {
      steps {
        script {
          withCredentials([file(credentialsId: 'gcp-service-account', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
            withCredentials([string(credentialsId: 'openai-api-key', variable: 'API_KEY')]) {
              withEnv([
                "DEEPSEEK_API_KEY=${API_KEY}",
              ]) {
                docker.image('kairyvu/mediline-ci:py3.13-make').inside {
                  sh 'make clean'
                  sh 'make venv'
                  sh 'make install'
                  sh 'make test'
                }
              }
            }
          }
        }
      post {
        always {
          junit 'reports/junit.xml'
        }
      }
    }
  }

  post {
    always {
      echo "Finished build #${env.BUILD_NUMBER}"
    }
  }
}
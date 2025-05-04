pipeline {
  agent any

  environment {
    GCP_SERVICE_ACCOUNT = credentials('gcp-service-account')
    OPENAI_API_KEY      = credentials('openai-api-key')
    TEST_DATABASE_URL = credentials('test-database-url')
  }

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
          docker.image('kairyvu/mediline-ci:py3.13-make').inside {
            sh 'export GOOGLE_APPLICATION_CREDENTIALS=$GCP_SERVICE_ACCOUNT'
            sh 'export DEEPSEEK_API_KEY=$OPENAI_API_KEY'
            sh 'export TEST_DATABASE_URL=$TEST_DATABASE_URL'
            sh 'make clean'
            sh 'make venv'
            sh 'make install'
            sh 'make test'
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
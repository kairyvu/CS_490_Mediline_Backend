pipeline {
  agent any
  
  options {
    buildDiscarder(logRotator(numToKeepStr: '10', daysToKeepStr: '7'))
  }

  stages {
    stage('Checkout') {
      steps {
        script {
          checkout scm
        }
      }
    }

    stage('Clean Workspace') {
      steps {
        cleanWs()
      }
    }

    stage('Build & Test in Docker') {
      steps {
        script {
          docker.image('kairyvu/mediline-ci:py3.13-make').inside {
            sh '''
              mkdir -p reports
              python -m venv venv
              . venv/bin/activate
              pip install --upgrade pip
              pip install -r requirements.txt
              pytest tests --junitxml=reports/junit.xml
              echo "=== REPORTS FOLDER CONTENTS ==="
              ls -R reports
            '''
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
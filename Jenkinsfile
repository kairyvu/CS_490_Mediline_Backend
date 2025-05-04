pipeline {
  agent any

  stages {
    stage('Build & Test in Docker') {
      steps {
        script {
          docker.image('kairyvu/mediline-ci:py3.13-make').inside {
            sh 'make venv'
            sh 'make install'
            sh 'pytest --junitxml=reports/junit.xml tests'
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
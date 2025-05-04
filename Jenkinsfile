pipeline {
  agent {
    docker {
      image 'kairyvu/mediline-ci:py3.13-make'
      args '-u root:root'
    }
  }

  environment {
    VENV = "${WORKSPACE}/venv"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Setup Virtualenv') {
      steps {
        sh 'make venv'
      }
    }

    stage('Install Dependencies') {
      steps {
        sh 'make install'
      }
    }

    stage('Unit Tests') {
      steps {
        sh 'python -m pytest tests'
      }
      post {
        always {
          junit 'reports/junit.xml'
        }
      }
    }
  }

  post {
    success {
      echo "Build #${env.BUILD_NUMBER} succeeded!"
    }
    failure {
      echo "Build #${env.BUILD_NUMBER} failed."
    }
    always {
      archiveArtifacts artifacts: 'reports/**/*.xml', allowEmptyArchive: true
    }
  }
}
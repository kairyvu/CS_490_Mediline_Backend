pipeline {
  agent any

  environment {
    REGISTRY = 'docker.io/youruser'
    IMAGE    = "${REGISTRY}/cs490-mediline-backend"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Install & Test') {
      steps {
        sh 'python -m venv .venv && . .venv/bin/activate'
        sh 'pip install -r requirements.txt'
        sh 'pytest tests'
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          // tag with build number for traceability
          dockerImage = docker.build("${IMAGE}:${env.BUILD_NUMBER}")
        }
      }
    }

    stage('Publish Image') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: '6d06a70b-40d8-4fff-ba14-9e95aa00bb2b',
          usernameVariable: 'DOCKERHUB_USER',
          passwordVariable: 'DOCKERHUB_PASS'
        )]) {
          sh "echo \"$DOCKERHUB_PASS\" | docker login -u \"$DOCKERHUB_USER\" --password-stdin"
          sh "docker push ${IMAGE}:${env.BUILD_NUMBER}"
        }
      }
    }

    stage('Deploy') {
      steps {
        // e.g. trigger a Kubernetes rollout or SSH-into-server script
        sh './deploy.sh ${IMAGE}:${env.BUILD_NUMBER}'
      }
    }
  }

  post {
    always {
      cleanWs()
    }
  }
}
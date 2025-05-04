FROM jenkins/jenkins:lts

USER root

RUN apt-get update \
 && apt-get install -y --no-install-recommends docker.io \
 && rm -rf /var/lib/apt/lists/*

RUN usermod -aG docker jenkins

USER jenkins
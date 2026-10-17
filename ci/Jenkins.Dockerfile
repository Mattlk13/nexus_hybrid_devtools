FROM docker.io/jenkins/jenkins:2.580.1-jdk21
RUN jenkins-plugin-cli --plugins matrix-auth:3.3

pipeline {
  agent any
  stages {
    stage('Checkout code') {
      steps {
        git(url: 'https://github.com/thanhthesheep/Library_DBMS', branch: 'main')
      }
    }

    stage('Print new message') {
      steps {
        echo 'Done checkout'
      }
    }

  }
}
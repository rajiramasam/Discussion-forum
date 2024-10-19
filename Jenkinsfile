pipeline{
  agent any
  triggers {
    githubPush() //Trigger on GitHub push
  }
  stages{
    stage('Checkout'){
      steps{
        checkout scm //Checkout the repository
      }
    }
  }
}

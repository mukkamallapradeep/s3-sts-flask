pipeline {
  agent any

  environment {
    AWS_REGION      = 'ap-south-1'
    SECRET_NAME     = 'prod/jenkins/aws-keys'
    ASSUME_ROLE_ARN = 'arn:aws:iam::<ACCOUNT_ID>:role/S3LimitedAccessRole'
    S3_BUCKET       = 'vms-lab-pradeep-logs'
    IMAGE_NAME      = 's3-sts-flask:latest'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Image') {
      steps {
        sh 'docker build -t $IMAGE_NAME .'
      }
    }

    stage('Run App') {
      steps {
        sh '''
          mkdir -p app_logs
          docker rm -f s3-sts-web || true
          docker run --name s3-sts-web -d \
            -p 8000:8000 \
            -e AWS_REGION=$AWS_REGION \
            -e SECRET_NAME=$SECRET_NAME \
            -e ASSUME_ROLE_ARN=$ASSUME_ROLE_ARN \
            -e S3_BUCKET=$S3_BUCKET \
            -v $(pwd)/app_logs:/app_logs \
            $IMAGE_NAME
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'app_logs/**', allowEmptyArchive: true
    }
  }
}

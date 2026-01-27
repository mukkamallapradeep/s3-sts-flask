pipeline {
  agent any

  environment {
    AWS_REGION      = 'ap-south-1'
    SECRET_NAME     = 'prod/jenkins/aws-keys'
    ASSUME_ROLE_ARN = 'arn:aws:iam::432870135296:role/S3LimitedAccessRole'
    S3_BUCKET       = 'vms-lab-pradeep-logs'
    IMAGE_NAME      = 's3-sts-flask:latest'
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/mukkamallapradeep/s3-sts-flask.git'
      }
    }

    stage('Build Image') {
      steps {
        sh 'docker build -t $IMAGE_NAME .'
      }
    }

    stage('Run App') {
      steps {
        withAWS(credentials: 'jenkins-aws-creds', region: "${AWS_REGION}", 
                // Optional: if you want Jenkins to assume a role before running app:
                // role: "${ASSUME_ROLE_ARN}", roleSessionName: "jenkins-s3-sts"
        ) {
          sh '''
            mkdir -p app_logs
            docker rm -f s3-sts-web || true
            # Pass the session creds from withAWS into container
            docker run --name s3-sts-web -d \
              -p 8000:8000 \
              -e AWS_REGION=$AWS_REGION \
              -e SECRET_NAME=$SECRET_NAME \
              -e ASSUME_ROLE_ARN=$ASSUME_ROLE_ARN \
              -e S3_BUCKET=$S3_BUCKET \
              -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
              -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
              -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
              -v $(pwd)/app_logs:/app_logs \
              $IMAGE_NAME
          '''
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'app_logs/**', allowEmptyArchive: true
    }
  }
}

node {
    stage('checkout scm') {
        checkout scm
    }
    stage('build') {
        def version = env.BUILD_ID
        sh 'tar -czf mwd-$BUILD_ID.tar.gz mwd order manage.py'
    }
}

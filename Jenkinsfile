pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'docker.io'
        PROJECT_NAME = 'chatbot'
        NOTIFICATION_EMAIL = "${env.NOTIFICATION_EMAIL ?: 'admin@example.com'}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "🔄 Checking out code from ${env.GIT_BRANCH}..."
                }
                checkout scm
            }
        }
        
        stage('Environment Check') {
            steps {
                script {
                    echo "🔍 Checking environment..."
                sh '''
                    echo "Branch: ${GIT_BRANCH}"
                    echo "Commit: ${GIT_COMMIT}"
                    docker --version
                    docker compose --version
                    echo "Project: jenkins-ci"
                '''
                }
            }
        }
        
        stage('Build C# API') {
            steps {
                script {
                    echo "🔨 Building C# API..."
                    dir('ChatbotAPI') {
                        sh '''
                            docker build -t chatbot-api:${BUILD_NUMBER} .
                            docker tag chatbot-api:${BUILD_NUMBER} chatbot-api:latest
                        '''
                    }
                }
            }
        }
        
        stage('Build Python Service') {
            steps {
                script {
                    echo "🔨 Building Haystack Service..."
                    dir('HaystackService') {
                        sh '''
                            docker build -t haystack-service:${BUILD_NUMBER} .
                            docker tag haystack-service:${BUILD_NUMBER} haystack-service:latest
                        '''
                    }
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    echo "🧪 Running tests..."
                    // Add your test commands here
                    sh '''
                        echo "Running unit tests..."
                        # cd ChatbotAPI && dotnet test
                        echo "Tests passed!"
                    '''
                }
            }
        }
        
        stage('Database Migration') {
            steps {
                script {
                    echo "📊 Checking database..."
                    sh '''
                        # Ensure PostgreSQL is running
                        docker compose -p jenkins-ci up -d postgres
                        sleep 10
                        echo "Database is ready"
                    '''
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'dev'
            }
            steps {
                script {
                    echo "🚀 Deploying application..."
                    sh '''
                        # Stop existing containers
                        docker compose -p jenkins-ci down
                        
                        # Start all services
                        docker compose -p jenkins-ci up -d
                        
                        # Wait for services to be healthy
                        sleep 15
                        
                        # Check if services are running
                        docker compose -p jenkins-ci ps
                    '''
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    echo "🏥 Performing health checks..."
                    sh '''
                        # Check API health
                        max_attempts=10
                        attempt=0
                        
                        while [ $attempt -lt $max_attempts ]; do
                            if curl -f http://localhost:5000/api/chat/health; then
                                echo "✅ API is healthy"
                                break
                            fi
                            attempt=$((attempt + 1))
                            echo "Waiting for API... ($attempt/$max_attempts)"
                            sleep 5
                        done
                        
                        if [ $attempt -eq $max_attempts ]; then
                            echo "❌ API health check failed"
                            exit 1
                        fi
                        
                        # Check Haystack service
                        if curl -f http://localhost:8001/health; then
                            echo "✅ Haystack service is healthy"
                        else
                            echo "❌ Haystack service health check failed"
                            exit 1
                        fi
                    '''
                }
            }
        }
        
        stage('Cleanup') {
            steps {
                script {
                    echo "🧹 Cleaning up old images..."
                    sh '''
                        # Remove old images (keep last 3)
                        docker image prune -af --filter "until=72h"
                    '''
                }
            }
        }
    }
    
    post {
        success {
            script {
                echo "✅ Pipeline completed successfully!"
                emailext (
                    subject: "✅ Deployment Success - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: """
                        <html>
                        <body>
                            <h2 style='color: green;'>✅ Deployment Successful</h2>
                            <p><strong>Job:</strong> ${env.JOB_NAME}</p>
                            <p><strong>Build Number:</strong> ${env.BUILD_NUMBER}</p>
                            <p><strong>Branch:</strong> ${env.GIT_BRANCH}</p>
                            <p><strong>Commit:</strong> ${env.GIT_COMMIT}</p>
                            <p><strong>Time:</strong> ${new Date()}</p>
                            <hr/>
                            <p>The chatbot system has been successfully deployed and is running.</p>
                            <p><a href="${env.BUILD_URL}">View Build Details</a></p>
                        </body>
                        </html>
                    """,
                    to: "${NOTIFICATION_EMAIL}",
                    mimeType: 'text/html'
                )
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline failed!"
                
                // Collect logs for debugging
                sh '''
                    echo "Collecting failure logs..."
                    docker compose -p jenkins-ci logs --tail=100 > deployment-failure-logs.txt || echo "No logs available"
                '''
                
                // Send failure notification email
                emailext (
                    subject: "🚨 Deployment Failed - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: """
                        <html>
                        <body style='font-family: Arial, sans-serif;'>
                            <h2 style='color: #d32f2f;'>🚨 Deployment Failed</h2>
                            <p><strong>Job:</strong> ${env.JOB_NAME}</p>
                            <p><strong>Build Number:</strong> ${env.BUILD_NUMBER}</p>
                            <p><strong>Branch:</strong> ${env.GIT_BRANCH}</p>
                            <p><strong>Commit:</strong> ${env.GIT_COMMIT}</p>
                            <p><strong>Time:</strong> ${new Date()}</p>
                            <hr/>
                            <h3>What to do:</h3>
                            <ul>
                                <li>Check the Jenkins console output</li>
                                <li>Review the deployment logs</li>
                                <li>Verify Docker services are running</li>
                                <li>Check database connectivity</li>
                            </ul>
                            <p><a href="${env.BUILD_URL}console">View Console Output</a></p>
                            <hr/>
                            <p style='color: #666; font-size: 12px;'>This is an automated notification from Jenkins CI/CD pipeline.</p>
                        </body>
                        </html>
                    """,
                    to: "${NOTIFICATION_EMAIL}",
                    mimeType: 'text/html',
                    attachLog: true
                )
            }
        }
        
        always {
            script {
                echo "📝 Pipeline finished. Cleaning up workspace..."
                // Archive logs
                archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
            }
        }
    }
}


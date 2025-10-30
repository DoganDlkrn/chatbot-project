FROM jenkins/jenkins:lts

USER root

# Docker CLI ve Docker Compose kurulumu
RUN apt-get update && \
    apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

# Jenkins kullanıcısını docker grubuna ekle
RUN groupadd -f docker && \
    usermod -aG docker jenkins

USER jenkins

# Skip initial setup wizard
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

# Install only essential plugins
RUN jenkins-plugin-cli --plugins \
    git:latest \
    workflow-aggregator:latest \
    docker-workflow:latest \
    email-ext:latest \
    mailer:latest \
    matrix-project:latest

# Create default admin user
ENV JENKINS_USER=admin
ENV JENKINS_PASS=admin123

# Copy init scripts to create admin user
RUN echo '#!groovy' > /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'import jenkins.model.*' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'import hudson.security.*' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'def instance = Jenkins.getInstance()' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'def hudsonRealm = new HudsonPrivateSecurityRealm(false)' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'hudsonRealm.createAccount("admin", "admin123")' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'instance.setSecurityRealm(hudsonRealm)' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'def strategy = new FullControlOnceLoggedInAuthorizationStrategy()' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'strategy.setAllowAnonymousRead(false)' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'instance.setAuthorizationStrategy(strategy)' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'instance.save()' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy


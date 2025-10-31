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
ENV JENKINS_USER=Dogandlkrn
ENV JENKINS_PASS=Dogandlkrn61

# Copy init scripts to create admin user
RUN echo '#!groovy' > /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'import jenkins.model.*' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'import hudson.security.*' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'def instance = Jenkins.getInstance()' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'def hudsonRealm = new HudsonPrivateSecurityRealm(false)' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'hudsonRealm.createAccount("Dogandlkrn", "Dogandlkrn61")' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'instance.setSecurityRealm(hudsonRealm)' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'def strategy = new FullControlOnceLoggedInAuthorizationStrategy()' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'strategy.setAllowAnonymousRead(false)' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'instance.setAuthorizationStrategy(strategy)' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy && \
    echo 'instance.save()' >> /usr/share/jenkins/ref/init.groovy.d/create-admin.groovy

# Configure SMTP for email notifications
RUN echo '#!groovy' > /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'import jenkins.model.*' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'import hudson.plugins.emailext.ExtendedEmailPublisher' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'def inst = Jenkins.getInstance()' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'def mailServer = inst.getDescriptor("hudson.plugins.emailext.ExtendedEmailPublisher")' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'mailServer.smtpHost = System.getenv("SMTP_HOST") ?: "smtp.gmail.com"' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'def smtpPort = (System.getenv("SMTP_PORT") ?: "465") as Integer' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'mailServer.smtpPort = smtpPort' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'mailServer.useSsl = (smtpPort == 465)' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'mailServer.smtpUsername = System.getenv("SMTP_USER")' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'mailServer.smtpPassword = System.getenv("SMTP_PASSWORD")' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'mailServer.charset = "UTF-8"' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'mailServer.defaultContentType = "text/html"' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'mailServer.save()' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'inst.save()' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy && \
    echo 'println("Email Extension SMTP configured successfully")' >> /usr/share/jenkins/ref/init.groovy.d/config-smtp.groovy


import jenkins.model.Jenkins
import jenkins.model.JenkinsLocationConfiguration

def jenkinsLocationConfiguration = JenkinsLocationConfiguration.get()
jenkinsLocationConfiguration.setAdminAddress("dogandalkiran53@gmail.com")
jenkinsLocationConfiguration.save()

println("Jenkins admin email configured")


import jenkins.model.Jenkins
import hudson.model.User
import hudson.model.Item
import hudson.security.*
import jenkins.security.ApiTokenProperty
import org.springframework.security.core.Authentication

def j = Jenkins.get()
def realm = new HudsonPrivateSecurityRealm(false)
j.setSecurityRealm(realm)
['cert-admin','cert-reader'].each { name ->
  def account = realm.createAccount(name, UUID.randomUUID().toString())
  def value = account.getProperty(ApiTokenProperty.class).tokenStore.generateNewToken('isolated-certification').plainValue
  account.save()
  new File('/var/jenkins_home/'+name+'.token').text = value
}
def strategy = new GlobalMatrixAuthorizationStrategy()
strategy.add(Jenkins.ADMINISTER, 'cert-admin')
strategy.add(Jenkins.READ, 'cert-reader')
strategy.add(Item.READ, 'cert-reader')
j.setAuthorizationStrategy(strategy)
j.setNumExecutors(0)
j.save()

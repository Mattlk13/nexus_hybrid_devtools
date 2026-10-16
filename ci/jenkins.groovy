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
j.setAuthorizationStrategy(new AuthorizationStrategy() {
  ACL getRootACL() {
    return new ACL() {
      boolean hasPermission2(Authentication a, Permission p) {
        return a.name == 'cert-admin' || (a.name == 'cert-reader' && (p == Jenkins.READ || p == Item.READ))
      }
    }
  }
  Collection<String> getGroups() { return [] }
})
j.setNumExecutors(0)
j.save()

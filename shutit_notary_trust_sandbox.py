import random
import string

from shutit_module import ShutItModule

class shutit_notary_trust_sandbox(ShutItModule):


	def build(self, shutit):
		vagrant_image = shutit.cfg[self.module_id]['vagrant_image']
		vagrant_provider = shutit.cfg[self.module_id]['vagrant_provider']
		gui = shutit.cfg[self.module_id]['gui']
		memory = shutit.cfg[self.module_id]['memory']
		module_name = 'shutit_notary_trust_sandbox_' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
		shutit.send('rm -rf /tmp/' + module_name + ' && mkdir -p /tmp/' + module_name + ' && cd /tmp/' + module_name)
		shutit.send('vagrant init ' + vagrant_image)
		shutit.send_file('/tmp/' + module_name + '/Vagrantfile','''
Vagrant.configure(2) do |config|
  config.vm.box = "''' + vagrant_image + '''"
  # config.vm.box_check_update = false
  # config.vm.network "forwarded_port", guest: 80, host: 8080
  # config.vm.network "private_network", ip: "192.168.33.10"
  # config.vm.network "public_network"
  # config.vm.synced_folder "../data", "/vagrant_data"
  config.vm.provider "virtualbox" do |vb|
    vb.gui = ''' + gui + '''
    vb.memory = "''' + memory + '''"
    vb.name = "shutit_notary_trust_sandbox"
  end
end''')
		shutit.send('vagrant up --provider virtualbox',timeout=99999)
		shutit.login(command='vagrant ssh')
		shutit.login(command='sudo su -',password='vagrant')
		shutit.install('apt-transport-https')
		shutit.install('ca-certificates')                                                                                                    
		shutit.send('apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D')
		shutit.send('touch /etc/apt/sources.list.d/docker.list')
		shutit.send('''cat > /etc/apt/sources.list.d/docker.list << END
deb https://apt.dockerproject.org/repo ubuntu-trusty main
END''')
		shutit.send('apt update -y')
		shutit.send('apt-cache policy docker-engine')
		shutit.install('docker-engine')
		shutit.send('curl -L https://github.com/docker/compose/releases/download/1.8.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose')
		shutit.send('chmod +x /usr/local/bin/docker-compose')
		shutit.send('''cat > docker-compose.yml << END
version: "2"
services:
  notaryserver:
    image: dockersecurity/notary_autobuilds:server-v0.3.0
    volumes:
      - notarycerts:/go/src/github.com/docker/notary/fixtures
    networks:
      - sandbox
    environment:
      - NOTARY_SERVER_STORAGE_TYPE=memory
      - NOTARY_SERVER_TRUST_SERVICE_TYPE=local
  sandboxregistry:
    image: registry:2.4.1
    networks:
      - sandbox
    container_name: sandboxregistry
  trustsandbox:
    image: docker:dind
    networks:
      - sandbox
    volumes:
      - notarycerts:/notarycerts
    privileged: true
    container_name: trustsandbox
    entrypoint: ""
    command: |-
        sh -c '
            cp /notarycerts/root-ca.crt /usr/local/share/ca-certificates/root-ca.crt &&
            update-ca-certificates &&
            dockerd-entrypoint.sh --insecure-registry sandboxregistry:5000'
volumes:
  notarycerts:
    external: false
networks:
  sandbox:
    external: false
END''')
		shutit.send('docker-compose up -d')
		shutit.login('docker exec -it trustsandbox sh')
		shutit.pause_point('')
		shutit.send('docker pull docker/trusttest')
		shutit.send('docker tag docker/trusttest sandboxregistry:5000/test/trusttest:latest')
		shutit.send('export DOCKER_CONTENT_TRUST=1')
		shutit.send('export DOCKER_CONTENT_TRUST_SERVER=https://notaryserver:4443')
		shutit.send('docker pull sandboxregistry:5000/test/trusttest')
		shutit.logout()
		shutit.send('docker logs trustsandbox')
		shutit.pause_point('')


		shutit.logout()
		shutit.logout()
		return True

	def get_config(self, shutit):
		shutit.get_config(self.module_id,'vagrant_image',default='ubuntu/trusty64')
		shutit.get_config(self.module_id,'vagrant_provider',default='virtualbox')
		shutit.get_config(self.module_id,'gui',default='false')
		shutit.get_config(self.module_id,'memory',default='1024')

		return True

	def test(self, shutit):

		return True

	def finalize(self, shutit):

		return True

	def isinstalled(self, shutit):

		return False

	def start(self, shutit):

		return True

	def stop(self, shutit):

		return True

def module():
	return shutit_notary_trust_sandbox(
		'imiell.shutit_notary_trust_sandbox.shutit_notary_trust_sandbox', 1243692531.0001,   
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup','shutit-library.virtualbox.virtualbox.virtualbox','tk.shutit.vagrant.vagrant.vagrant']
	)

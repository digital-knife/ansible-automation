pipeline {
    agent {
        kubernetes {
            inheritFrom 'terraform-cloud-provisioner'
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: ansible
    image: python:3.9-slim
    command: ['cat']
    tty: true
'''
        }
    }
    
    parameters {
        string(
            name: 'inventory_path',
            defaultValue: 'ansible/inventory/local.ini',
            description: 'Path to Ansible inventory file'
        )
        
        booleanParam(
            name: 'dry_run',
            defaultValue: false,
            description: 'Run in check mode (no actual changes)'
        )
        
        string(
            name: 'ansible_user',
            defaultValue: 'root',
            description: 'SSH user for target hosts'
        )
        
        string(
            name: 'extra_vars',
            defaultValue: '',
            description: 'Additional Ansible variables (key=value key2=value2)'
        )
    }
    
    environment {
        ANSIBLE_HOST_KEY_CHECKING = 'False'
        ANSIBLE_FORCE_COLOR = 'true'
    }
    
    stages {
        stage('Setup') {
            steps {
                container('ansible') {
                    echo "=================================================="
                    echo "Security Hardening Pipeline"
                    echo "=================================================="
                    echo "Inventory: ${params.inventory_path}"
                    echo "Dry Run: ${params.dry_run}"
                    echo "SSH User: ${params.ansible_user}"
                    echo "=================================================="
                    
                    sh '''
                        apt-get update -qq
                        apt-get install -y -qq openssh-client sshpass > /dev/null 2>&1
                        python3 -m pip install --upgrade pip > /dev/null 2>&1
                        pip install ansible-core
                    '''
                    
                    sh 'ansible-galaxy collection install -r ansible/requirements.yml'
                    
                    echo "✓ Dependencies installed"
                }
            }
        }
        
        stage('Validate Inventory') {
            steps {
                container('ansible') {
                    sh """
                        ansible-inventory -i ${params.inventory_path} --list
                    """
                    echo "✓ Inventory validated"
                }
            }
        }
        stage('Run Hardening') {
            steps {
                container('ansible') {
                    script {
                        def ansibleCmd = "ansible-playbook playbooks/main.yml -i ${params.inventory_path}"
                        
                        // Add dry-run flag
                        if (params.dry_run) {
                            ansibleCmd += " --check"
                        }
                        
                        // Add extra vars if provided
                        if (params.extra_vars) {
                            ansibleCmd += " --extra-vars '${params.extra_vars}'"
                        }
                        
                        // Add SSH user
                        ansibleCmd += " -u ${params.ansible_user}"
                        
                        echo "Executing: ${ansibleCmd}"
                        
                        // Copy SSH key from credential
                        withCredentials([file(credentialsId: 'docker-ssh-key', variable: 'SSH_KEY')]) {
                            sh """
                                mkdir -p ~/.ssh
                                cp \$SSH_KEY ~/.ssh/id_rsa
                                chmod 600 ~/.ssh/id_rsa
                                cd ansible
                                ${ansibleCmd} --private-key ~/.ssh/id_rsa
                            """
                        }
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "=================================================="
            echo "✓ Security hardening completed successfully"
            echo "=================================================="
        }
        failure {
            echo "=================================================="
            echo "✗ Security hardening failed - check logs above"
            echo "=================================================="
        }
    }
}
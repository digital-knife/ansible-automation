pipeline {
    agent {
        kubernetes {
            inheritFrom 'terraform-cloud-provisioner'
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: python
    image: python:3.9-slim
    command: ['cat']
    tty: true
'''
        }
    }
    
    parameters {
        choice(
            name: 'target_mode',
            choices: ['manual', 'dynamic_aws', 'static_inventory'],
            description: '''Target Selection Mode:
- manual: Specify single IP/hostname/instance-id
- dynamic_aws: Auto-discover EC2 instances by tags
- static_inventory: Use predefined inventory file'''
        )
        
        string(
            name: 'manual_target',
            defaultValue: '',
            description: 'Single target (IP/hostname/i-xxxxx) - only for manual mode'
        )
        
        string(
            name: 'aws_tag_filter',
            defaultValue: 'Role=web',
            description: 'AWS tag filter for dynamic mode (e.g., Role=web, Environment=prod)'
        )
        
        string(
            name: 'static_inventory_path',
            defaultValue: 'ansible/inventory/local.ini',
            description: 'Path to inventory file - only for static_inventory mode'
        )
        
        booleanParam(
            name: 'dry_run',
            defaultValue: false,
            description: 'Run in check mode (no actual changes)'
        )
        
        booleanParam(
            name: 'skip_validation',
            defaultValue: false,
            description: 'Skip validation after hardening'
        )
    }
    
    environment {
        REPORTS_DIR = 'reports'
        ANSIBLE_HOST_KEY_CHECKING = 'False'
    }
    
    stages {
        stage('Setup') {
            steps {
                container('python') {
                    echo "=================================================="
                    echo "Security Hardening Pipeline"
                    echo "=================================================="
                    echo "Target Mode: ${params.target_mode}"
                    
                    script {
                        if (params.target_mode == 'manual') {
                            echo "Manual Target: ${params.manual_target}"
                        } else if (params.target_mode == 'dynamic_aws') {
                            echo "AWS Tag Filter: ${params.aws_tag_filter}"
                        } else {
                            echo "Static Inventory: ${params.static_inventory_path}"
                        }
                    }
                    
                    echo "Dry Run: ${params.dry_run}"
                    echo "Skip Validation: ${params.skip_validation}"
                    echo "=================================================="
                    
                    // Install system dependencies
                    sh """
                        apt-get update -qq
                        apt-get install -y -qq openssh-client sshpass > /dev/null 2>&1
                    """
                    
                    // Setup Python environment
                    sh """
                        python3 -m pip install --upgrade pip > /dev/null 2>&1
                        pip install -r requirements.txt
                        ansible-galaxy collection install -r ansible/requirements.yml
                    """
                    
                    echo "✓ Dependencies installed"
                }
            }
        }
        
        stage('Validate Parameters') {
            steps {
                container('python') {
                    script {
                        if (params.target_mode == 'manual' && !params.manual_target) {
                            error("Manual mode requires 'manual_target' parameter")
                        }
                        if (params.target_mode == 'static_inventory' && !params.static_inventory_path) {
                            error("Static inventory mode requires 'static_inventory_path' parameter")
                        }
                    }
                    echo "✓ Parameters validated"
                }
            }
        }
        
        stage('Run Hardening') {
            steps {
                container('python') {
                    script {
                        def hardeningCmd = "python3 harden.py"
                        
                        // Build command based on mode
                        if (params.target_mode == 'manual') {
                            hardeningCmd += " --target ${params.manual_target}"
                        } else if (params.target_mode == 'dynamic_aws') {
                            hardeningCmd += " --dynamic-aws"
                            env.TAG_FILTER = params.aws_tag_filter
                        } else {
                            hardeningCmd += " --inventory ${params.static_inventory_path}"
                        }
                        
                        // Add optional flags
                        if (params.dry_run) {
                            hardeningCmd += " --dry-run"
                        }
                        
                        echo "Executing: ${hardeningCmd}"
                        
                        // Copy SSH key from credential
                        withCredentials([file(credentialsId: 'docker-ssh-key', variable: 'SSH_KEY')]) {
                            sh """
                                cp \$SSH_KEY /tmp/ssh-key
                                chmod 600 /tmp/ssh-key
                                ${hardeningCmd}
                            """
                        }
                    }
                }
            }
        }
        
        stage('Validate Hardening') {
            when {
                expression { params.skip_validation == false }
            }
            steps {
                container('python') {
                    script {
                        def inventoryPath
                        
                        if (params.target_mode == 'manual') {
                            // Use temp inventory created by harden.py
                            inventoryPath = sh(
                                script: "ls /tmp/ansible-*.ini 2>/dev/null | head -1 || echo 'ansible/inventory/local.ini'",
                                returnStdout: true
                            ).trim()
                        } else if (params.target_mode == 'dynamic_aws') {
                            inventoryPath = 'ansible/inventory/aws_ec2.yml'
                        } else {
                            inventoryPath = params.static_inventory_path
                        }
                        
                        echo "Running validation against: ${inventoryPath}"
                        sh "python3 scripts/validate.py --inventory ${inventoryPath}"
                    }
                }
            }
        }
        
        stage('Generate Report') {
            when {
                expression { params.skip_validation == false }
            }
            steps {
                container('python') {
                    sh 'python3 scripts/report.py reports/validation-report.json'
                    echo "✓ HTML report generated"
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'reports/*.json, reports/*.html, reports/*.log', allowEmptyArchive: true
            
            echo "=================================================="
            echo "Pipeline Complete"
            echo "Check archived artifacts for detailed results"
            echo "=================================================="
        }
        success {
            echo "✓ Security hardening completed successfully"
        }
        failure {
            echo "✗ Security hardening failed - check logs above"
        }
    }
}
# How to deploy ec2

## 1. Navigate to this directory

## 2. Generate the keys
Run `ssh-keygen -t rsa -b 4096 -m pem -f capstone_kp && openssl rsa -in capstone_kp -outform pem && mv capstone_kp capstone_kp.pem && chmod 400 capstone_kp.pem`

## 3. Add your ip address to the secrets
Run
`echo -e "my_ip_address = \x22$(curl https://checkip.amazonaws.com)\x22 " >> secrets.tfvars`

## 4. Initialise terraform project
Run
`terraform init`

## 5. Validate terraform script
Run
`terraform validate`

## 6. Plan terraform script
Run
`terraform plan -var-file=secrets.tfvars`

## 7. Apply terraform script
Run
`terraform apply -var-file=secrets.tfvars`

## 8. Clean up
Run
`terraform destroy -var-file=secrets.tfvars`
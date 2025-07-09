# Docker Workshop Cloud Deployment Lifecycle

## AWS EC2 Instances (x86, US East)

Prod instances

| Notes           | Instance   | vCPU | RAM    | Cost/hr | 3 hr  | 24 hr  |
| --------------- | ---------- | ---- | ------ | ------- | ----- | ------ |
| **Production**  | r5.2xlarge | 8    | 64 GiB | $0.504  | $1.51 | $12.10 |
| Dev (alt CPU)   | m5.2xlarge | 8    | 32 GiB | $0.384  | $1.15 | $9.22  |
| Dev (burstable) | t3.2xlarge | 8    | 32 GiB | $0.333  | $1.00 | $7.99  |

Maybe  c5.9xlarge (36 vCPU, 72GB, $1.53/hour).

Added an EBS vol for extra space for docker builds..

Dev instances

| Instance      | vCPU | RAM    | Cost/hr |
| ------------- | ---- | ------ | ------- |
| **r5.xlarge** | 4    | 32 GiB | $0.252  |
| **r5.large**  | 2    | 16 GiB | $0.126  |
| **m5.large**  | 2    | 8 GiB  | $0.096  |
| **t3.large**  | 2    | 8 GiB  | $0.0832 |
| **t3a.large** | 2    | 8 GiB  | $0.0752 |

t3a is AMD

## Launch

```bash
cd infra/
terraform init
terraform apply -auto-approve
cd ..
docker-compose up -d
cloudflared tunnel --config infra/cf-config-prod.yml run docker-workshop
```

## Verify

```bash
# Get outputs
terraform output

# Test API endpoint
curl https://api.docker-workshop.com/session/health

# Check SSL certificates
curl -I https://api.docker-workshop.com
```

## During Pres

### Backend Updates

(user might be ec2-user dep on if i change stuff)

```bash
ssh -i infra/.ssh/workshop_key ubuntu@$(terraform output -raw aws_eip.workshop.public_ip)
# or
aws ssm start-session --target $(terraform output -raw instance_id)

cd talks
git pull
docker-compose restart
```

## Post-Workshop Cleanup


```bash
# Tear down cloud
cd infra/
terraform destroy -auto-approve
# Stop cloudflared tunnel
# Stop local services
docker-compose down
```

## Emergency Scenarios

### Cloud Instance Issues

```bash
# Check instance status
terraform output ssh_command
ssh ubuntu@<ip>

# View logs
sudo journalctl -u nginx
docker-compose logs

# Restart everything
sudo systemctl restart nginx
docker-compose restart
```

### DNS/SSL Issues

```bash
# SSH to instance
# Check nginx config
sudo nginx -t

# Renew SSL if needed
sudo certbot renew --nginx

# Check Cloudflare DNS
nslookup api.docker-workshop.com
```

### Scale Issues During Workshop

```bash
# Monitor resources on cloud instance
htop
docker stats

# 1. Stop terraform destroy
# 2. Edit terraform.tfvars: instance_type = "c5.9xlarge"
# 3. terraform apply
```

## Quick Reference

### URLs

- **Slides**: https://docker-workshop.com (local)
- **API/WebSocket**: https://api.docker-workshop.com (cloud)
- **SSH**: `ssh ubuntu@$(terraform output -raw instance_ip)`

### Key Commands

```bash
# Deploy
terraform apply -auto-approve

# Destroy
terraform destroy -auto-approve

# Check status
terraform output
curl https://api.docker-workshop.com/session/health

# Update slides (local)
# Just edit files - changes are instant

# Update backend (cloud)
ssh ubuntu@<ip>
cd workshop && git pull && docker-compose restart
```

## Terraform commnds

Stop/start EC2:

```bash
# Stop instance
terraform apply -target=aws_instance.workshop -var="instance_type=t3.nano"

# Start with original size
terraform apply -target=aws_instance.workshop -var="instance_type=c5.4xlarge"
```

Destroy/recreate EC2:

```bash
# Destroy EC2 and EIP association
terraform destroy -target=aws_instance.workshop -target=aws_eip_association.workshop

# Recreate
terraform apply -target=aws_instance.workshop -target=aws_eip_association.workshop
```

Update just CF

```bash
terraform apply -target=cloudflare_record.workshop_main -target=cloudflare_record.workshop_api
```

Check what instance type we stood up w/

```bash
terraform show | grep instance_type
terraform output -json | jq
aws ec2 describe-instances --instance-ids $(terraform output -raw instance_ip) --query 'Reservations[0].Instances[0].InstanceType'
```

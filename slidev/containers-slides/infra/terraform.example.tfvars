# AWS EC2 Instances (x86, US East)

# | Use Case       | Instance        | vCPU | RAM     | Cost/hr | 3 hr   | 24 hr   | Notes                                 |
# |----------------|-----------------|------|---------|---------|--------|---------|---------------------------------------|
# | **Production** | r5.2xlarge      | 8    | 64 GiB  | $0.504  | $1.51  | $12.10  | Best for RAM-heavy workloads          |
# | **Dev (ideal)**| r5.xlarge       | 4    | 32 GiB  | $0.252  | $0.76  | $6.05   | Same memory ratio as prod             |
# | Dev (alt CPU)  | m5.2xlarge      | 8    | 32 GiB  | $0.384  | $1.15  | $9.22   | More CPU, general-purpose             |
# | Dev (burstable)| t3.2xlarge      | 8    | 32 GiB  | $0.333  | $1.00  | $7.99   | CPU throttles; OK for light workloads |

# curl "https://api.cloudflare.com/client/v4/user/tokens/verify" -H "Authorization: Bearer <token>"

repo_url             = "https://github.com/Marco-Christiani/talks"
domain               = "docker-workshop.com"
cloudflare_api_token = "..."
cloudflare_zone_id   = "..."
aws_region           = "us-east-1"
# instance_type = "c5.4xlarge"
instance_type = "r5.xlarge"

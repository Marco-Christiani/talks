output "instance_id" {
  value = aws_instance.workshop.id
}

output "instance_ip" {
  value = aws_eip.workshop.public_ip
}

output "workshop_url" {
  value = "https://${var.domain}"
}

output "api_url" {
  value = "https://api.${var.domain}"
}

output "ssh_command" {
  # Might need to lossen the key reqs: -o PubkeyAcceptedAlgorithms=+ssh-rsa -o HostKeyAlgorithms=+ssh-rsa
  value = "ssh -i .ssh/workshop_key ubuntu@${aws_eip.workshop.public_ip}"
}

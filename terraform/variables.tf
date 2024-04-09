variable "domain_name" {}
variable "project_name" {}
variable "sshkey" {}

data "digitalocean_ssh_key" "oceanbreeze" {
  name = var.sshkey
}
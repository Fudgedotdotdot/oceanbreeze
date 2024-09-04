variable "domain_name" {}
variable "project_name" {}
variable "sshkey" {}
variable "droplet_ip" {
  type = string
  default = ""
}
variable "spawn_droplet" {
  type = number
  default = 1
}

data "digitalocean_ssh_key" "oceanbreeze" {
  name = var.sshkey
}
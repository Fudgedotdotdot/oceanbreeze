resource "digitalocean_droplet" "oceanbreeze" {
    count = var.spawn_droplet == 1 ? 1 : 0
    image = "ubuntu-20-04-x64"
    name = var.domain_name
    region = "ams3"
    #size = "s-1vcpu-512mb-10gb" golang needs 1GB of ram to build custom caddy binary
    size = "s-1vcpu-1gb"
    ssh_keys = [
      data.digitalocean_ssh_key.oceanbreeze.id
    ]    
}
resource "digitalocean_domain" "oceanbreeze" {
  name = var.domain_name
}
# example A with wildcard
resource "digitalocean_record" "wildcard" {
  domain = digitalocean_domain.oceanbreeze.id
  type   = "A"
  name   = "*"
  value  = digitalocean_droplet.oceanbreeze.ipv4_address
}
# example A
resource "digitalocean_record" "main" {
  domain = digitalocean_domain.oceanbreeze.id
  type   = "A"
  name   = "@"
  value  = digitalocean_droplet.oceanbreeze.ipv4_address
}
# example dmarc
resource "digitalocean_record" "dmarc" {
  domain = digitalocean_domain.oceanbreeze.id
  type   = "TXT"
  name   = "_dmarc"
  value  = "v=DMARC1; p=none; rua=mailto:dmarc@${var.domain_name}"
}
# example spf
resource "digitalocean_record" "spf" {
  domain = digitalocean_domain.oceanbreeze.id
  type   = "TXT"
  name   = "@"
  value  = "v=spf1 include:spf.infomaniak.ch a:${var.domain_name} ip4:${digitalocean_droplet.oceanbreeze.ipv4_address} -all"
}
# example mx
resource "digitalocean_record" "mx" {
  domain   = digitalocean_domain.oceanbreeze.id
  type     = "MX"
  name     = "@"
  priority = 10
  value    = "mta-gw.infomaniak.ch."
}


data "digitalocean_project" "oceanbreeze" {
  name = var.project_name
}

resource "digitalocean_project_resources" "oceanbreeze_domain" {
  project = data.digitalocean_project.oceanbreeze.id
  resources = [digitalocean_domain.oceanbreeze.urn]
}

resource "digitalocean_project_resources" "oceanbreeze_droplet" {
  project = data.digitalocean_project.oceanbreeze.id
  resources = can(digitalocean_droplet.oceanbreeze[0].urn) ? [digitalocean_droplet.oceanbreeze[0].urn] : []
}
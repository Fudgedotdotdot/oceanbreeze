data "digitalocean_project" "oceanbreeze" {
  name = var.project_name
}

resource "digitalocean_project_resources" "oceanbreeze" {
  project = data.digitalocean_project.oceanbreeze.id
  resources = [
    digitalocean_droplet.oceanbreeze.urn,
    digitalocean_domain.oceanbreeze.urn
  ]
}

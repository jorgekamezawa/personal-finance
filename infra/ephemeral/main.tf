# Both come from the persistent layer. Looking them up by name makes creating the server
# fail when that layer is missing, instead of bringing up a machine with no firewall.
data "hcloud_firewall" "closed" {
  name = "${var.name}-closed"
}

data "hcloud_ssh_key" "admin" {
  name = "${var.name}-admin"
}

# What lets the server join the private network by itself, already tagged.
# Single use and short lived: it ends up in the state, and by then it is worthless.
# Ephemeral, so the network forgets the server soon after it is gone and the next one keeps the name.
# No comma in the description: the network refuses the key with "invalid characters".
resource "tailscale_tailnet_key" "server" {
  reusable      = false
  ephemeral     = true
  preauthorized = true
  expiry        = 900
  description   = "${var.name} server single use"
  tags          = ["tag:financas-server"]
}

resource "hcloud_server" "app" {
  name        = var.name
  image       = "ubuntu-24.04"
  server_type = var.server_type
  location    = var.location

  # With a key registered the provider creates no root password.
  ssh_keys     = [data.hcloud_ssh_key.admin.id]
  firewall_ids = [data.hcloud_firewall.closed.id]

  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }

  user_data = templatefile("${path.module}/cloud-init.yaml", {
    name        = var.name
    app_user    = var.app_user
    swap_gb     = var.swap_gb
    network_key = tailscale_tailnet_key.server.key
  })
}

output "machine" {
  description = "Type and city that were actually created"
  value       = "${hcloud_server.app.server_type} @ ${hcloud_server.app.location}"
}

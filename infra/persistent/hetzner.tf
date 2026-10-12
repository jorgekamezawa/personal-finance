# With a key registered, a new server is created without a root password sent by email.
resource "hcloud_ssh_key" "admin" {
  name       = "${var.name}-admin"
  public_key = var.ssh_public_key
}

# No rule block on purpose: with no inbound rule nothing from the internet gets in.
# The private network still works because the server opens the connection outwards.
resource "hcloud_firewall" "closed" {
  name = "${var.name}-closed"
}

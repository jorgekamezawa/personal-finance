# Ephemeral layer: the server, created and destroyed on demand.
# Its state is separate from the persistent layer, so destroying here cannot reach the database copies.

terraform {
  required_version = "~> 1.15.0"

  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "1.70.0"
    }
    tailscale = {
      source  = "tailscale/tailscale"
      version = "0.29.2"
    }
  }

  # Same bucket as the persistent layer, another key. See that layer for why each flag is there.
  backend "s3" {
    bucket = "personal-finance-tfstate"
    key    = "ephemeral/terraform.tfstate"
    region = "auto"

    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true
    use_path_style              = true
    use_lockfile                = true
  }
}

# HCLOUD_TOKEN comes from the environment.
provider "hcloud" {}

# TAILSCALE_OAUTH_CLIENT_ID and TAILSCALE_AUDIENCE come from the environment: the CI proves
# who it is to the private network, and no secret is stored.
provider "tailscale" {}

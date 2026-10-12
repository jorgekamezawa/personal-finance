# Persistent layer: what is never destroyed when the environment is turned off.
# The server lives in another folder with its own state, so destroying it cannot reach this one.

terraform {
  required_version = "~> 1.15.0"

  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "1.70.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "5.27.0"
    }
  }

  # The state holds secrets, so it stays out of the bucket the server can read.
  # The endpoint comes from AWS_ENDPOINT_URL_S3: a backend block accepts no variable.
  backend "s3" {
    bucket = "personal-finance-tfstate"
    key    = "persistent/terraform.tfstate"
    region = "auto"

    # R2 speaks the S3 protocol but has no account lookup, region list or metadata service.
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true
    use_path_style              = true

    # Lock file next to the state: a second run fails instead of overwriting the first.
    use_lockfile = true
  }
}

# Each provider reads its token from the environment: HCLOUD_TOKEN and CLOUDFLARE_API_TOKEN.
provider "hcloud" {}

provider "cloudflare" {}

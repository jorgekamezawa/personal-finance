# While the environment is destroyed, this bucket is the only place the data exists.
resource "cloudflare_r2_bucket" "backups" {
  account_id = var.cloudflare_account_id
  name       = "${var.name}-backups"
  location   = "weur"

  # Declared intent: a destroy on this layer fails instead of deleting the copies.
  lifecycle {
    prevent_destroy = true
  }
}

# Retention lock: whatever key is used, a copy cannot be deleted or overwritten before it ages out.
resource "cloudflare_r2_bucket_lock" "backups" {
  account_id  = var.cloudflare_account_id
  bucket_name = cloudflare_r2_bucket.backups.name

  rules = [{
    id      = "retain-every-copy"
    enabled = true
    condition = {
      type            = "Age"
      max_age_seconds = var.backup_retention_days * 24 * 60 * 60
    }
  }]
}

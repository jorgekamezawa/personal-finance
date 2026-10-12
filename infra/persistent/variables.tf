variable "name" {
  description = "Project name, prefix of everything created here"
  type        = string
  default     = "personal-finance"
}

variable "cloudflare_account_id" {
  description = "Cloudflare account that owns the buckets (TF_VAR_cloudflare_account_id)"
  type        = string
}

variable "ssh_public_key" {
  description = "Public key registered at the server provider (TF_VAR_ssh_public_key)"
  type        = string
}

variable "backup_retention_days" {
  description = "Days a database copy stays locked against deletion and overwrite"
  type        = number
  default     = 30
}

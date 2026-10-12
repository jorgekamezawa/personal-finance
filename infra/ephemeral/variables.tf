variable "name" {
  description = "Project name: the server name and the name it answers to on the private network"
  type        = string
  default     = "personal-finance"
}

variable "server_type" {
  description = "Machine type. Written by choose-machine.sh from the real stock; no default on purpose"
  type        = string
}

variable "location" {
  description = "City of the datacenter. Written by choose-machine.sh"
  type        = string
}

variable "app_user" {
  description = "User that runs the application: no sudo, member of the docker group"
  type        = string
  default     = "finance"
}

variable "swap_gb" {
  description = "Swap in GB. The machine comes with none, and a JVM out of memory is killed without it"
  type        = number
  default     = 2
}

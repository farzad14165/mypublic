variable "esxi_hostname" {
  description = "ESXi server host name."
  default     = "172.20.8.138"
  sensitive = true
}

variable "esxi_hostport" {
  description = "ESXi server port."
  default     = "22"
}

variable "esxi_hostssl" {
  description = "ESXi server SSH port."
  default     = "443"
}

variable "esxi_username" {
  description = "ESXi server user name."
  default     = "root"
}

variable "esxi_password" {
  description = "ESXi server password."
  sensitive = true
}

variable "nodes" {
  type        = list(tuple([string, string]))
  description = "IP addresses and names of VMs."
  default     = [
    ["172....", "vm2"],
    ["172....", "vm3"],
    # Add more IP addresses and names here
  ]
}

variable "ssh_public_key_path" {
  type        = string
  default = "~/.ssh/id_rsa.pub"
}

variable "ssh_private_key_path" {
  type        = string
  default = "~/.ssh/id_rsa"
  sensitive   = true
}

variable "default_password" {
  type      = string
  sensitive = true
}

variable "default_ssh_user" {
  type    = string
  default = "ubuntu"
}
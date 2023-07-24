provider "esxi" {
  esxi_hostname = var.esxi_hostname
  esxi_hostport = var.esxi_hostport
  esxi_hostssl  = var.esxi_hostssl
  esxi_username = var.esxi_username
  esxi_password = var.esxi_password
}

resource "random_id" "instance_id" {
  byte_length = 8
}

resource "esxi_guest" "default" {
  count = length(var.nodes)

  guest_name     = var.nodes[count.index][1]
  numvcpus       = 2
  memsize        = 4096
  boot_disk_size = 40
  disk_store     = "datastore1"

  network_interfaces {
    virtual_network = "VM Network"
	ip_address       = var.nodes[count.index][0]
  }

  ovf_source = "https://cloud-images.ubuntu.com/releases/22.04/release/ubuntu-22.04-server-cloudimg-amd64.ova"

  ovf_properties {
    key   = "instance-id"
    value = random_id.instance_id.hex
  }

  ovf_properties {
    key   = "hostname"
    value = var.nodes[count.index]
  }

  ovf_properties {
    key   = "password"
    value = var.default_password
  }

#  provisioner "file" {
#    source      = "/home/sadmin/hi.txt"
#    destination = "/tmp/hi.txt"
#
#    connection {
#     type        = "ssh"
#      host        = "127.0.0.1"
#      user        = var.default_ssh_user
#      private_key = file(var.ssh_private_key_path)
#      timeout     = "15s"
#    }
#  }

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      host        = self.ip_address
      user        = var.default_ssh_user
      private_key = file(var.ssh_private_key_path)
      timeout     = "15s"
    }

    inline = [
      "echo '${var.default_password}' | sudo -S hostnamectl set-hostname ${var.nodes[count.index]}",
      "echo '${var.default_password}' | sudo -S apt update",
      "echo '${var.default_password}' | sudo -S apt upgrade -y",
      "echo '${var.default_password}' | sudo -S apt clean"
    ]
  }
}








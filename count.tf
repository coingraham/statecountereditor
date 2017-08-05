# Terraform count state generator

provider "aws" {
  region              = "us-east-1"
  profile             = "firstwatch"
  allowed_account_ids = ["955241386426"]
}

variable "test_tags" {
  default = [ "ebs2", "ebs3" ]
}

variable "another_tags" {
  default = [ "ebs1", "ebs2", "ebs4", "ebs5", "ebs6" ]
}

resource "aws_ebs_volume" "test" {
  count = "${length(var.test_tags)}"
  availability_zone    = "us-east-1a"
  type                 = "gp2"
  size                 = 1
  tags {
      Name = "${var.test_tags[count.index]}"
  }
}

resource "aws_ebs_volume" "another" {
  count = "${length(var.another_tags)}"
  availability_zone    = "us-east-1a"
  type                 = "gp2"
  size                 = 1
  tags {
      Name = "${var.another_tags[count.index]}"
  }
}

resource "aws_ebs_volume" "lastly" {
  availability_zone    = "us-east-1a"
  type                 = "gp2"
  size                 = 1
  tags {
      Name = "NonCount"
  }
}
# Terraform count state generator

provider "aws" {
  region              = "us-east-1"
  profile             = "firstwatch"
}

variable "test_tags" {
  default = [ "ebs1", "ebs2", "ebs3" ]
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

variable "another_tags" {
  default = [ "ebs1", "ebs2", "ebs3", "ebs4", "ebs5", "ebs6" ]
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
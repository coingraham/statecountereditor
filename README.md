# statecountereditor
Edit the terraform state to remove an item from the count and maintain existing systems. 

# Purpose
This utility is to assist terraform users when they are utilizing the count functionality and need to make changes that will shift the items in a list.

# Start Here
Clone the repo to a folder and open the files.

# Explaining Terraform count problem
If you take a look at the example count.tf terraform, you'll see the following definition:

```variable "test_tags" {
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
}```

This will create three EBS volumes with the name tags ebs1, ebs2, and ebs3 and is a very cool feature in terraform.  This allows you to easily create some automation scripts to build a lot of resources.  In the terraform state file, they will be listed as "aws_ebs_volume.test.0", "aws_ebs_volume.test.1", "aws_ebs_volume.test.2".  The issue is that if in the future you decide that you no longer need ebs2.  For clarity, here is the current mapping in our example:

```Volume to state resource
ebs1 = "aws_ebs_volume.test.0"
ebs2 = "aws_ebs_volume.test.1"
ebs3 = "aws_ebs_volume.test.2"```

If you remove ebs2 from the array, then ebs3 will shift into ebs2's place in the array.  This will cause terraform to see the following when you run terraform plan:

```Volume to state resource
ebs1 = "aws_ebs_volume.test.0"
ebs3 = "aws_ebs_volume.test.1" (rename ebs2 tag to ebs3)
nothing = "aws_ebs_volume.test.2" (delete ebs3)```

Here's the actual terraform plan for this:

```~ aws_ebs_volume.test.1
    tags.Name: "ebs2" => "ebs3"

- aws_ebs_volume.test.2```

So while we wanted to remove ebs2, terraform will actually delete ebs3 and rename ebs2 to ebs3.  This issue is further complicated by the fact that there is no way to edit the state file for counters with the terraform state command.  It won't take in commands with the designation like "aws_ebs_volume.test.0".  This isn't a huge deal with ebs volumes and tags, but if it were instances and AMIs, all your systems from that item forward would likely be rebuild in the wash.

# One solution
The simplest solution is to open the state file and change it manually.  In our example above, you simply need to find "aws_ebs_volume.test.1" and delete it.  Then edit all the counters going forward and reduce their ending count digit by one.

# Enter statecountereditor
So I've created a python script that will introspect the state file and find all the counters that you're using.  Then it will prompt you for which one to modify.  Once you decide which counter definition you want to modify you'll pick which item you want to remove.  The script will then present you with the item for you to validate it is correct.  If it is the correct item, that item will be removed and all subsequent items will be reduced one digit to the end.  The old state will be saved as "terraform.tfstate.original-%m-%d-%y-%H%M%S" and your new state written as terraform.tfstate.  Then you can remove the item from your terraform config and run terraform plan (there should be no changes)

# Author
Coin Graham




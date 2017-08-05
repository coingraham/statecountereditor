import json
import re
import os
import time
from countable import Countable


class StateCounterHelper:

    def __init__(self):

        self.countable_dict = {}
        self.menu_dict = {}
        self.state_file_name = "terraform.tfstate"
        self.count_pattern = r"\"(.*\..*\.\d+)\":"
        self.json_state = None

    def main(self):

        # Read the state file if we can, quit if we cannot
        try:
            state_file = open(self.state_file_name, "r")
            state_info = state_file.read()

        except Exception as read_exception:
            print "Could not read state file with error:\n{}".format(read_exception)
            return 0

        # Create a json object for the state file and iterator based on the search string
        self.json_state = json.loads(state_info)
        count_iter = re.finditer(self.count_pattern, state_info)

        # Go through the matches and create counter objects for each.  Save in a dict for later
        for count in count_iter:
            count_group = str(count.group(1))
            count_resource = count_group.split(".")[0]
            count_name = count_group.split(".")[1]
            count_value = count_group.split(".")[2]
            resource_name = ".".join(count_group.split(".")[0:2])

            if resource_name in self.countable_dict:
                self.countable_dict[resource_name]["Countable"].push(count_value)

            else:
                countable_obj = Countable(count_resource, count_name)
                self.countable_dict[resource_name] = {
                    "Countable": countable_obj
                }
                countable_obj.push(count_value)

        # Only proceed if there are countable objects that can be modified
        if Countable.total > 0:
            countable_id = 1
            for resource_name in self.countable_dict:
                self.menu_dict[str(countable_id)] = self.countable_dict[resource_name]
                countable_id += 1

            os.system('clear')

            # Present the Menu options to decide with resource to modify
            print "Please choose the countable resource you want to modify:\n"

            # Build the menu from the countable objects
            for menu_item in self.menu_dict.keys():
                countable = self.menu_dict[menu_item]["Countable"]
                print "{}. {} with {} items".format(menu_item, countable.get_full_name(), countable.get_max())

            print "\n0. Quit"

            # Get the user input
            choice = raw_input(" >>  ")

            # Return the user input
            return choice

        # If there are no countable objects return 0 which will effectively quit the program
        else:
            return 0

    def menu_selection(self, choice):

        # Quit out if the choice is 0
        if choice == 0:
            print "Quitting."
            return

        # Find the countable object for the choice and prompt for which item to remove
        if choice in self.menu_dict.keys():
            countable = self.menu_dict[choice]["Countable"]
            full_name = countable.get_full_name()
            resource_max = countable.get_max()

            # Prompt for which item to remove
            print "\nModifying {} with {} items.  Which item would you like to remove " \
                  "(just put the number and remember it starts with 0)?".format(full_name, resource_max)

            # Get the user input
            item_to_remove = raw_input(" >>  ")

            # Send the input to the function for removal
            self.find_item_to_remove(full_name, item_to_remove, countable)

    def find_item_to_remove(self, full_name, item_to_remove, countable):

            # Setup the name for use later
            resource_name = full_name + "." + item_to_remove

            # Check for existance of the item requested, otherwise quit
            if resource_name in self.json_state["modules"][0]["resources"]:
                resource_definition = self.json_state["modules"][0]["resources"][resource_name]
            else:
                print "Resource {} does not exist!  Exiting.".format(resource_name)
                return

            os.system('clear')

            # Get input on the item to remove
            print "Do you want to remove {} with the following definition?".format(resource_name)

            print json.dumps(resource_definition, indent=4, sort_keys=True)

            # Get input from the user
            answer = raw_input(" Type Yes to Remove, "
                               "Previous to see the previous item, "
                               "or Next to see the next item >>  ")

            # Move up one item and ask again
            if answer == "Next":
                item_to_remove = str(int(item_to_remove) + 1)
                self.find_item_to_remove(full_name, item_to_remove, countable)

            # Move back one item and ask again
            if answer == "Previous":
                item_to_remove = str(int(item_to_remove) - 1)
                self.find_item_to_remove(full_name, item_to_remove, countable)

            # Advance with the removal of the item
            if answer == "Yes":

                # Walk through the items from the selected to the end and move them back one step
                for item in range(int(item_to_remove), int(countable.get_max())):
                    resource_name = full_name + "." + str(item)
                    next_resource_name = full_name + "." + str(item + 1)

                    # If there is a next item, save to this item
                    if next_resource_name in self.json_state["modules"][0]["resources"]:
                        self.json_state["modules"][0]["resources"][resource_name] = \
                            self.json_state["modules"][0]["resources"][next_resource_name]

                    # If there isn't a next item, we're at the end and will delete it.
                    else:
                        self.json_state["modules"][0]["resources"].pop(resource_name)

                # Try to rename the existing state file and save the new state file.
                try:
                    # Use time so that the new file name is unique and not overwritten.
                    time_string = time.strftime("%m-%d-%y-%H%M%S")
                    original_filename = "terraform.tfstate.original-{}".format(time_string)
                    os.rename("terraform.tfstate", original_filename)
                    f = open("terraform.tfstate", "w")
                    f.write(json.dumps(self.json_state, indent=4, sort_keys=True))
                    print "Original state moved to \"{}\" and state file updated.".format(original_filename)

                except Exception as e:
                    print "Error {} trying to rename the state file.".format(e)

            # If they don't follow instructions quit
            else:
                print "Please follow the instructions."
                return


if __name__ == '__main__':

    # Create the base object
    my_sch = StateCounterHelper()

    # Get the main resource to modify
    my_choice = my_sch.main()

    # Pick the item and do the action
    my_sch.menu_selection(my_choice)

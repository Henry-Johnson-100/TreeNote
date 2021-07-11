import TreeNote as tn
import cmd
import os
import sys


def __get_platform_commands() -> dict:
    command_dict = dict()
    platform = os.name
    if platform == "posix":
        command_dict = {
            "clear": "clear"
        }
    else:
        command_dict = {
            "clear": "cls"
        }
    return command_dict


PRJ_TOP = tn.main()
CURRENT_PRJ = None
CURRENT_PRJ = PRJ_TOP
CONFIG_FILE_NAME = "tree.conf"
COMMANDS = __get_platform_commands()

class PrjCmd(cmd.Cmd):
    # cmd instance vars here
    prompt = "~: "

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.top = tn.main()
        self.prj = self.top
        self.buffer = None
        # TODO find a better way to handle the getcwd() jank
        self.path = os.getcwd().replace("\\", "/") + "/"
        self.file = str()
        self.config = self.__open_config()
        self.config_options = self.__init_config_options()
        self.__parse_config()
        self.intro = (
            """
        ************************************************************************
        *                                                                      *
        *                              TREE NOTE                               *
        *                                                                      *
        ************************************************************************
        """
        )

    @staticmethod
    def __arg_contains(arg_str: str, *contain_str: str) -> bool:
        """:
            Return True if a passed keyword is found in the passed argument string.

            Args:
                arg_str (str): Argument string collected from a do_...() method.
                *contain_str (tuple: str): Strings to check for in the arg string.

            Returns:
                bool: True if any string in *contain_str is found in arg_str
            """
        contains = True
        for field in contain_str:
            if field not in arg_str:
                contains = False
        return contains

    @staticmethod
    def __first_arg_is(arg_str: str, contain_str: str) -> bool:
        split_arg = arg_str.split(" ")
        if len(split_arg) == 0:
            return False
        if split_arg[0] != contain_str:
            return False
        return True

    @staticmethod
    def __arg_strip(arg_str: str, str_to_strip: str, delimiter_to_split: str = " ") -> dict:
        """:
            Return list of remaining arguments from passed arg_string

            Args:
                arg_str (str): The arg string collected from a do_...() method
                str_to_strip (str): The string to remove from the arg string
                delimiter_to_split (str, optional): delimiter on which to split the arg string. Defaults to " ".

            Returns:
                dict: Keys containing the stripped arguments, values are all True.
            """
        arg_dict = dict()
        remaining_str = arg_str
        if str_to_strip in arg_str and str_to_strip != "":
            remaining_str = arg_str.replace(str_to_strip, "")
        remaining_list = remaining_str.split(delimiter_to_split)
        for arg_key in remaining_list:
            arg_dict[arg_key] = True
        return arg_dict

    @staticmethod
    def __is_empty_arg(arg_str: str) -> bool:
        return len(arg_str) == 0 or arg_str.isspace()

    @staticmethod
    def __init_config_options() -> dict:
        return {
            "print_options": ""
        }

    def __open_config(self, mode: str = "r"):
        try:
            config = open(CONFIG_FILE_NAME, mode)
        except OSError:
            config = open(CONFIG_FILE_NAME, "x")
            config.close()
            config = open(CONFIG_FILE_NAME, mode)
        return config

    def __close_config(self):
        pass

    def __reopen_config_if_not_mode(self, mode: str):
        if self.config.mode != mode:
            self.config.close()
            self.config = self.__open_config(mode)

    def __parse_config(self) -> None:
        self.__reopen_config_if_not_mode("r")
        config_list = self.config.readlines()
        split_config_line = list()
        for config_line in config_list:
            split_config_line = str(config_line).split(" ")
            if split_config_line[0] in self.config_options:
                self.config_options[split_config_line[0]] = str(
                    " ").join(split_config_line[1:])

    def __save_config(self) -> None:  # Only called on do_quit()
        self.__reopen_config_if_not_mode("w")
        config_lines = list()
        for config_key in self.config_options:
            config_lines.append(
                " ".join([config_key, self.config_options[config_key]]))
        self.config.writelines(config_lines)
        self.config.close()

    def __is_valid_arg(self, arg_str: str, arg_to_test: str, delimiter_to_split: str = " ") -> tuple:
        return self.__arg_contains(arg_str, arg_to_test), self.__arg_strip(arg_str, arg_to_test, delimiter_to_split)

    def __print_tree(self, **kwargs) -> None:
        """:
            Print method for displaying the tree with some extra options.

            Arguments:
            clear: bool (True) - clears the terminal when printing.
            overview: bool (False) - prints the entire tree instead of the tree starting from the current branch.
            """
        if kwargs.setdefault("clear", True):
            os.system(COMMANDS.get("clear"))
        if kwargs.setdefault("overview", False):
            print(self.top.__str_tree__(**kwargs))
        else:
            print(self.prj.__str_tree__(**kwargs))

    def __is_file_set_and_arg_empty(self, arg: str) -> bool:
        """:
            Returns True if self.file is not empty and the passed arg is not empty.

            Args:
                arg (str): The argument collected from a do_...() method

            Returns:
                bool: True if self.file and arg are not empty
            """
        return len(self.file) != 0 and (self.__is_empty_arg(arg))

    def __list_dir(self) -> list:
        def filter_rule(x): return x.find(".pkl") != -1
        file_list = list()
        for (dirpath, dirname, filename) in os.walk(self.path):
            file_list.extend(filename)
        return list(filter(filter_rule, file_list))

    def __str_dir(self) -> str:
        file_list = self.__list_dir()
        file_str = str()
        for thing in filter(lambda x: x.find(".py") == -1, file_list):
            file_str += thing + "\n"
        return file_str

    def __select_from_list(self, select_list: list):
        if len(select_list) == 0:
            return None
        elif len(select_list) == 1:
            return select_list[0]
        for i in range(0, len(select_list)):
            print(i + 1, str(select_list[i]))
        select_input = input("select: ")
        if select_input.isnumeric():
            if int(select_input) in range(1, len(select_list) + 1):
                return select_list[int(select_input) - 1]
        else:
            return None

    def do_new(self, arg):
        self.prj = self.prj.def_subproject(arg)
        self.__print_tree()

    def help_new(self):
        print(
            "Create a new branch nested below the current branch" +
            "\nArgs: Name of the new branch."
        )

    def do_paste(self, arg):  # Do not paste something twice lol #TODO doesn't recursively past all of an object's subprojects too, see the bug example file
        if self.buffer is None:
            return None
        self.prj = self.prj.paste_subproject(self.buffer)  # This may not work
        self.__print_tree()

    def do_cut(self, arg):
        self.buffer = self.prj
        self.prj = self.prj.clear_project()
        self.__print_tree()

    def do_out(self, arg):
        if self.prj.parent.layer >= -1:
            self.prj = self.prj.parent
            self.__print_tree()
        else:
            self.__print_tree()

    def help_out(self):
        print("Move one layer out of the tree, to the previous branch.")

    def do_in(self, arg):
        subprojects = self.prj.get_subprojects()
        down_choice = self.__select_from_list(subprojects)
        if down_choice is None:
            return
        self.prj = down_choice
        self.__print_tree()

    def help_in(self):
        print("Move one layer into the tree."
              "\nIf multiple branches are available, a list will be presented to choose from."
              )

    def do_top(self, arg):
        self.prj = self.top
        self.__print_tree()

    def help_top(self):
        print("Go to the top of the tree.")

    def do_description(self, arg):
        self.prj.set_description(arg)
        self.__print_tree()

    def help_description(self):
        print("Enter a description for the current branch.")

    def do_print(self, arg):
        if self.__first_arg_is(arg, "here"):
            self.__print_tree(
                **self.__arg_strip(((arg + self.config_options.setdefault("print_options", ""))),
                                   "here"
                                   )
            )
        elif self.__first_arg_is(arg, "file"):
            print(self.file)
        elif self.__first_arg_is(arg, "dir"):
            print(self.__str_dir())
        elif self.__first_arg_is(arg, "config"):
            print(self.config_options)
        else:
            self.__print_tree(
                **self.__arg_strip(((arg + " overview " + self.config_options.setdefault("print_options", ""))),
                                   ""
                                   )
            )

    def help_print(self):
        print(
            "Displays the entire tree, according to additional arguments or options set with \'config print\'"
            "\nSee \'?config print\' for additional options."
            "\nArguments: \'here\' - displays the tree at the current branch and all lower branches."
            "\nfile - displays the current filename."
            "\ndir - displays all of the current files in the directory."
        )

    def do_clear(self, arg):
        self.prj = self.prj.clear_project()
        self.__print_tree()

    def help_clear(self):
        print("Remove the current branch and all lower branches from the tree.")

    def do_reset(self, arg):
        self.top = tn.main()
        self.prj = self.top
        self.__print_tree()

    def help_reset(self):
        print("Removes all branches from the current tree.")

    def do_save(self, arg: str):
        file_name = str()
        if self.__is_file_set_and_arg_empty(arg):
            tn.save(self.top, self.path + self.file)
            file_name = self.file
        else:
            tn.save(self.top, self.path + arg)
            file_name = arg
        print("Saved to " + file_name)

    def help_save(self):
        print("Saves the current tree to the file given as an argument or if no arg is given, to the current file shown by \'print file\'.")

    def do_load(self, arg):
        del self.top
        del self.prj
        file_name = str()
        if self.__is_file_set_and_arg_empty(arg):
            self.top = tn.load(self.path + self.file)
            file_name = self.file
        else:
            self.top = tn.load(self.path + arg)
            file_name = arg
        print("Loaded from " + file_name)
        self.prj = self.top
        self.__print_tree(overview=True)

    def help_load(self):
        print("Loads a tree from the file given as an argument or if no arg is given, from the current file shown by \'print file\'.")

    def do_file(self, arg):
        file_name = str()
        if self.__is_empty_arg(arg):
            select = self.__select_from_list(self.__list_dir())
            if select is None:
                return
            self.file = select
        else:
            if arg.find(".pkl") == -1:
                arg += ".pkl"
            self.file = arg
        print("file name set to " + self.file)

    def help_file(self):
        print("Sets the current file to the name given as an argument. If no arg is given, a list of files in the current directory is shown to choose from.")

    def do_priority(self, arg):
        if self.__is_empty_arg(arg):
            priority_dict = {
                tn.Fore.WHITE + "Default" + tn.Style.RESET_ALL: "0",
                tn.Fore.MAGENTA + "Low" + tn.Style.RESET_ALL: "1",
                tn.Fore.CYAN + "Medium" + tn.Style.RESET_ALL: "3",
                tn.Fore.YELLOW + "High" + tn.Style.RESET_ALL: "5",
                tn.Fore.RED + "Critical" + tn.Style.RESET_ALL: "6"
            }
            priority_str = self.__select_from_list(list(priority_dict))
            self.prj.do_recursive(lambda prj: prj.set_priority(priority_dict.setdefault(
                priority_str, "0")))  # this is so cool that this works lol
        else:
            self.prj.set_priority(arg)
        self.__print_tree()

    def help_priority(self):
        print("Sets the priority of the branch, giving it an integer value and a text color"
              "\nArgs:"
              "\n(int) 0-6"
              "\nNone - a list will be presented with options to choose from."
              )

    def do_move(self, arg):
        if arg == "up" or arg == "down":
            self.prj.move_laterally({"up": -1, "down": 1}.get(arg))
        elif arg == "in" or arg == "out":
            # self.prj.move_vertically({"in": -1, "out": 1}.get(arg)) #This needs some work
            pass
        else:
            return

    def help_move(self):
        print("Moves a branch, can only move to locations which are under the same branch as the original location"
              "\nup - move branch upwards."
              "\ndown = move branch downwards."
              )

    def do_tag(self, arg):
        if self.__arg_contains(arg, "remove"):
            remove_list = list(self.__arg_strip(arg, "remove").keys())
            for tag in remove_list:
                self.prj.unset_tag(tag)
        else:
            self.prj.set_tag(arg)
        self.__print_tree(tags=True)

    def help_tag(self):
        print("Set a tag to the current branch.")

    def do_date(self, arg):
        self.prj.set_date(arg)

    def help_date(self):
        print("Set a date to the current branch.")

    def do_search(self, arg):
        search_tags = self.__arg_strip(arg, "")

    def do_filter(self, arg):
        pass

    def do_config(self, arg):
        if self.__first_arg_is(arg, "print"):
            self.config_options["print_options"] = str(
                arg).replace("print", "")

        elif self.__first_arg_is(arg, "clear"):
            if self.__is_empty_arg(str(arg).replace("clear", "")):
                config_options_list = list()
                for key in self.config_options:
                    config_options_list.append(str(key))
                # I think this will return a string
                self.config_options[self.__select_from_list(
                    config_options_list)] = ""
            else:
                configs_to_clear = self.__arg_strip(arg, "clear")
                for config_to_clear_key in configs_to_clear:
                    if config_to_clear_key in self.config_options:
                        self.config_options[config_to_clear_key] = ""

    def help_config(self):
        print("various configurations - fill in at a later date")

    def do_quit(self, arg):
        self.__save_config()
        sys.exit()

    def help_quit(self):
        print("Quits")

    def emptyline(self):
        return


CLI = PrjCmd()
CLI.cmdloop()

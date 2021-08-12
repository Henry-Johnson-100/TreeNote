from typing import IO
import TreeNote as tn
import cmd
import os
import sys
import pickle


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
DEFAULT_CONFIG = {
    "print_options": [],
    "aliases": {}
}
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
        self.config = dict()
        self.intro = (
            """
        ************************************************************************
        *                                                                      *
        *                              TREE NOTE                               *
        *                                                                      *
        ************************************************************************
        """
        )

    def preloop(self) -> None:
        try:
            config = open(CONFIG_FILE_NAME, "rb")
        except OSError:
            config = open(CONFIG_FILE_NAME, "x")
            config.close()
            config = open(CONFIG_FILE_NAME, "rb")
        try:
            self.config = pickle.load(config)
        except EOFError:
            self.config = dict()
        db = set(self.config.keys())
        if set(self.config.keys()) != set(DEFAULT_CONFIG.keys()):
            self.config.update(**{"print_options":[], "aliases":{}})
        config.close()


    def precmd(self, line: str) -> str:
        split_line = line.split(" ")
        if split_line[0] in self.config["aliases"]:
            cmd_name = self.config["aliases"][split_line[0]]
            cmd_str = f"do_{cmd_name}"
            if hasattr(self, cmd_str):
                cmd_args = " ".join(split_line[1:])
                return f"{cmd_name} {cmd_args}"
        return line

    def __save_config(self) -> None:
        config = open(CONFIG_FILE_NAME, "wb")
        pickle.dump(self.config,config)
        config.close()

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
        """:
            True if the first argument in a space-delimited arg string is the same as the passed parameter

            Args:
                arg_str (str): space delimited string of arguments to check
                contain_str (str): The specific argument keyword to check for

            Returns:
                bool: True if the first argument in arg_str is the same as contain_str, False otherwise
            """        
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
        """:
            Check if an argument string is empty.

            Args:
                arg_str (str): argument string to check

            Returns:
                bool: True if the argument string is empty or only spaces
            """        
        return len(arg_str) == 0 or arg_str.isspace()

    def __is_valid_arg(self, arg_str: str, arg_to_test: str, delimiter_to_split: str = " ") -> tuple:
        #DOCME
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
        #DOCME
        def filter_rule(x): return x.find(".pkl") != -1
        file_list = list()
        for (dirpath, dirname, filename) in os.walk(self.path):
            file_list.extend(filename)
        return list(filter(filter_rule, file_list))

    def __str_dir(self) -> str:
        #DOCME
        file_list = self.__list_dir()
        file_str = str()
        for thing in filter(lambda x: x.find(".py") == -1, file_list):
            file_str += thing + "\n"
        return file_str

    def __select_from_list(self, select_list: list):
        #DOCME
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
        #DOCME
        self.prj = self.prj.def_subproject(arg)
        self.__print_tree()

    def help_new(self):
        print(
            "Create a new branch nested below the current branch" +
            "\nArgs: Name of the new branch."
        )

    def do_paste(self, arg):  # Do not paste something twice lol #TODO doesn't recursively paste all of an object's subprojects too, see the bug example file
        #DOCME
        if self.buffer is None:
            return None
        self.prj = self.prj.paste_subproject(self.buffer)  # This may not work
        self.__print_tree()

    def do_cut(self, arg):
        #DOCME
        self.buffer = self.prj
        self.prj = self.prj.clear_project()
        self.__print_tree()

    def do_out(self, arg):
        #DOCME
        if self.prj.parent.layer >= -1:
            self.prj = self.prj.parent
            self.__print_tree()
        else:
            self.__print_tree()

    def help_out(self):
        print("Move one layer out of the tree, to the previous branch.")

    def do_in(self, arg):
        #DOCME
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
        #DOCME
        self.prj = self.top
        self.__print_tree()

    def help_top(self):
        print("Go to the top of the tree.")

    def do_description(self, arg):
        #DOCME
        self.prj.set_description(arg)
        self.__print_tree()

    def help_description(self):
        print("Enter a description for the current branch.")

    def do_print(self, arg):
        #DOCME
        if self.__first_arg_is(arg, "here"):
            self.__print_tree(
                **self.__arg_strip(((arg + " ".join(self.config["print_options"]))),
                                   "here"
                                   )
            )
        elif self.__first_arg_is(arg, "file"):
            print(self.file)
        elif self.__first_arg_is(arg, "dir"):
            print(self.__str_dir())
        elif self.__first_arg_is(arg, "config"):
            print(self.config)
        else:
            self.__print_tree(
                **self.__arg_strip(((arg + " overview " + " ".join(self.config["print_options"]))),
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
        #DOCME
        self.prj = self.prj.clear_project()
        self.__print_tree()

    def help_clear(self):
        print("Remove the current branch and all lower branches from the tree.")

    def do_reset(self, arg):
        #DOCME
        self.top = tn.main()
        self.prj = self.top
        self.__print_tree()

    def help_reset(self):
        print("Removes all branches from the current tree.")

    def do_save(self, arg: str):
        #DOCME
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
        #DOCME
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
        #DOCME
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
        #DOCME
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

    def do_move(self, arg): #TODO
        #DOCME
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
                self.prj.do_recursive(lambda prj: prj.unset_tag(tag))
        else:
            tag_list = list(self.__arg_strip(arg, "").keys())
            for tag in tag_list:
                self.prj.do_recursive(lambda prj: prj.set_tag(tag))
                # self.prj.set_tag(arg)
        self.__print_tree(tags=True)

    def help_tag(self):
        print("Set a tag to the current branch.")

    def do_date(self, arg):#TODO
        self.prj.set_date(arg)

    def help_date(self):#TODO
        print("Set a date to the current branch.")

    def do_search(self, arg):#TODO #XXX
        search_tags = self.__arg_strip(arg, "")

    def do_filter(self, arg):
        pass

    def do_config(self, arg):
        if self.__first_arg_is(arg, "print_options"):
            self.config["print_options"].extend(str(arg).replace("print_options", "").strip().split(" ")) 
        elif self.__first_arg_is(arg, "aliases"):
            argKeys = str(arg).replace("aliases","").strip().split(" ")
            self.config["aliases"][argKeys[0]] = argKeys[1]
        elif self.__first_arg_is(arg, "clear"):
            if not self.__is_empty_arg(str(arg).replace("clear","")):
                configs_to_clear = self.__arg_strip(arg, "clear")
                for config_to_clear_key in configs_to_clear:
                    if config_to_clear_key in self.config:
                        self.config[config_to_clear_key] = DEFAULT_CONFIG[config_to_clear_key]
            else:
                print("Please supply arguments of the configuration options you wish to be cleared.")


    def help_config(self):
        print("""Set the configurations:\n
            The first argument to the 'config' command should be the key of the config you would like to change,
            The second argument is the value that goes along with that key.
            \tChanging config keys varies in behavior depending on the key, the print_options key can accept multiple arguments.
            \tThe aliases key can only accept one, that is a key value pair.\n
            OPTIONS:
            \t-> print_options : [tags,date,highlight]
            \t-> aliases : 'alias name' 'operation'
        """)

    def do_quit(self, arg):
        #DOCME
        self.__save_config()
        sys.exit()

    def help_quit(self):
        print("Quits")

    def emptyline(self) -> None:
        #DOCME
        return


CLI = PrjCmd()
CLI.cmdloop()

import pickle
import io
from colorama import init
from colorama import Fore, Back, Style


class Project:
    """Contains titles, descriptions, due dates, tags, and subprojects or tasks."""

    def __init__(self, title: str, layer: int, parent_project: 'Project'):
        self.title = title
        self.layer = layer
        self.parent = parent_project
        self.subprojects = list()

        self.description = str()
        self.tags = set()
        self.date = str()
        if self.parent is not None:
            self.priority = self.parent.priority
        else:
            self.priority = "0"

    def get_title(self) -> str:
        return self.title

    def get_layer(self) -> int:
        return self.layer

    def get_description(self) -> str:
        return self.description

    def get_parent(self) -> 'Project':
        return self.parent

    def get_subprojects(self) -> list:
        return self.subprojects

    def get_priority(self) -> str:
        return self.priority

    def get_tags(self) -> str:
        return ", ".join(self.tags)

    def get_date(self) -> str:
        return self.date

    def get_priority_text_color(self) -> str:
        """:
            Returns the Colorama.Fore string containing the ANSI code for the color corresponding to a priority level.

            Returns:
                str: ANSI code contained in Colorama.Fore() object, a string.
            """
        return {
            "0": Fore.WHITE,  # Neutral priority
            "1": Fore.MAGENTA,
            "2": Fore.BLUE,
            "3": Fore.CYAN,
            "4": Fore.GREEN,
            "5": Fore.YELLOW,
            "6": Fore.RED
        }.get(self.priority)

    def get_layer_prefix(self) -> str:
        correction = 1
        if self.layer == 0:
            correction = 0
        return str().join(["-"] * (self.layer * 4 - correction)) + ">"

    def get_layer_description_spacing(self) -> str:
        return str().join([" "] * (self.layer * 4))

    def set_description(self, description: str) -> None:
        self.description = str().join(
            [" "] * (self.layer * 4)) + description  # + "\n"

    def set_tag(self, tag: str) -> None:
        self.tags.add(tag)

    def unset_tag(self, tag: str) -> None:
        if tag in self.tags:
            self.tags.remove(tag)

    def set_date(self, date: str) -> None: #TODO Need to make this a datetime instead of str
        self.date = date

    def set_priority(self, priority: str) -> None:
        """:
            Set's priority attribute of a branch. Between 0 and 6.

            Args:
                priority (str): A string of the integer indicating the priority.
            """
        priority = str(priority)
        lower = "0"
        upper = "6"
        if priority < lower:
            priority = lower
        if priority > upper:
            priority = upper
        self.priority = priority

    def clear_project(self) -> 'Project':
        """:
            Clears, or removes, a branch by removing it from its parent's index.

            Returns:
                Project: The parent branch of the cleared branch.
            """
        parent_project = self.parent
        self.parent.subprojects.remove(self)
        return parent_project

    # found a workaround in vscode to hide doc_strings
    def def_subproject(self, title: str) -> 'Project':
        """:
            Creates a new Project instance nested in the self.subprojects list and one layer lower.

            Args:
                title (str): Title of the new Project.

            Returns:
                Project: New Project object, initialized with the entered title and layer = self.layer + 1
            """
        sub_project = Project(title, self.layer + 1, self)
        self.subprojects.append(sub_project)
        return sub_project

    def paste_subproject(self, prj: 'Project') -> 'Project':  # Who knows about this
        prj.parent_project = self
        prj.layer = prj.parent_project.layer
        #prj.layer = prj.parent_project.layer + 1
        def __increment_layer(prj):
            prj.layer = prj.layer + 1
        prj.do_recursive(lambda prj: __increment_layer(prj))
        self.subprojects.append(prj)
        return prj

    def walk_tree(self, subproject_tree_list: list, top_layer: int = 0) -> list:
        """:
            Returns a list of Project instances and PLACEHOLDER of all the subprojects located further down the tree.
            \nPLACEHOLDER indicate a new subproject that is only nested in the top layer.

            Args:
                subproject_tree_list (list): pass empty list: list()
                top_layer (int, optional): leave default, will be replaced by the top layer internally. Defaults to 0.

            Returns:
                list: List of all Projects located down the tree
            """
        if len(subproject_tree_list) == 0:
            top_layer = self.layer
        subproject_tree_list.append(self)
        for subproject in self.subprojects:
            subproject.walk_tree(subproject_tree_list, top_layer)
        if self.layer == top_layer:
            return subproject_tree_list

    def move_laterally(self, direction: int) -> 'Project':
        """:
            Moves branches laterally. 
            Lateral movement is across the same layer. Branches are essentially just moved in the parent branch's subproject list index.

            Returns:
                Project: The parent of the branch that has been moved.
            """
        if direction == 0:
            return
        direction = int(abs(direction) / direction)
        if self.parent is None:
            return
        parent = self.parent
        current_pos = parent.subprojects.index(self)
        next_pos = current_pos + direction
        self.clear_project()
        parent.subprojects.insert(next_pos, self)
        return parent

    def move_vertically(self, direction: int) -> None:
        if direction == 0:
            return
        direction = int(abs(direction) / direction)
        if direction > 0 and self.parent.parent is None:
            return
        elif direction < 0 and self.parent is None:
            return
        parent = {1: self.parent.parent, -1: self.parent}.get(direction)
        blank_branch = parent.def_subproject("")
        self.clear_project()
        blank_branch.subprojects.insert(0, self)

    def do_recursive(self, doFunc=lambda x: x) -> None:
        """:
            Takes a function as an arg and performs it recursively on all objects descended from the current one

            Args:
                doFunc (function, optional): Function to perform, takes a Project object as an argument. Defaults to lambda x:x.
            """
        doFunc(self)
        if len(self.subprojects) == 0:
            return
        for subproject in self.subprojects:
            subproject.do_recursive(doFunc)

    def __str_subprojects__(self) -> str:
        subproject_str = str()
        for subproject in self.subprojects:
            subproject_str += str(subproject)
        return subproject_str

    def __str_tree__(self, **kwargs) -> str:
        """Prints the current project and each project of a lower layer."""
        tree = self.walk_tree(list())
        tree_str = str()
        for subproject in tree:
            if subproject.layer != self.layer:
                tree_str += subproject.__str_f__(**kwargs) + "\n"
            else:
                tree_str += subproject.__str_f__(**kwargs) + "\n"
        return tree_str

    def __str_f__(self, **kwargs: bool) -> str:
        """:
            [summary]

            Kwargs:
                highlight [bool]: If the text is highlighted (False)
                ellipsis [bool]: If description text is truncated with an ellipsis. (False)
                priority [bool]: If priority number is displayed (False)
                tags [bool]: Display tags (False)
                date [bool]: Display date (False)

            Returns:
                str: [description]
            """
        print_str = ""
        print_str += self.get_layer_prefix()

        if kwargs.setdefault("highlight", False):
            print_str += Back.MAGENTA

        print_str += self.get_priority_text_color()
        print_str += self.get_title()

        if kwargs.setdefault("priority", False):
            print_str += " (priority: " + str(self.get_priority()) + ")"
        if kwargs.setdefault("tags", False):
            print_str += " (tags: " + self.get_tags() + ")"
        if kwargs.setdefault("date", False):
            print_str += " (date: " + self.get_date() + ")"

        print_str += Style.RESET_ALL

        if len(self.get_description()) == 0:
            descr_string = ""
        elif kwargs.setdefault("ellipsis", False):
            descr_string = "\n" + \
                           self.get_description()[0: 10].rstrip() + "..."
        else:
            descr_string = "\n" + self.get_description()

        print_str += descr_string
        return print_str

    def __str__(self):
        return self.__str_f__(ellpisis=True)

    def __eq__(self, o: object) -> bool:
        pass

    @staticmethod
    def __pickle__(file):
        """returns the given project object in pickle format."""
        pass


def main():
    init()
    return Project("Notes", -1, None)


def save(Prj: Project, filepath: str) -> None:
    file = open(filepath, "wb")
    pickle.dump(Prj, file)
    file.close()


def load(filepath: str) -> Project:
    file = open(filepath, "rb")
    return pickle.load(file)


if __name__ == "__main__":
    test = Project("test", 0, None)

    def test1():
        test = Project("test", 0, None)
        test.set_priority("5")
        test.set_tag("cool")
        test.set_tag("good")
        test.set_description(
            "Something to describe this test branch and test some features of __print_f__()")
        test.date = "5/29/2021"
        print(test.__str_f__(date=True, highlight=True, ellipsis=True, tags=True))

    def do_recur_test():
        test.def_subproject("test_sub_1").def_subproject(
            "test_sub_2").def_subproject("test_sub_3")
        test.def_subproject("test_sub_a_1").def_subproject("test_sub_a_2")
        print(test.__str_tree__())
        test.do_recursive(lambda prj: print("hi"))

    do_recur_test()

"""TDGam Component, sub-class of TDGamContainer."""
import re
import json
import logging
from pprint import pformat

from .plugins import TouchDesigner
from .container import TDGamContainer


class TDGamComponent(TDGamContainer):
    """Class to interface with the selection of ops by the user.

    These ops need to be converted to JSON and destroyed, then
    re-created again on the fly. This class is only responsible for
    dealing with functionality on the selection of ops and their data.

    This class is intended as the main interface with the user and
    their application.
    """

    def __init__(self, selection, name):
        """Create a component from the selected ops.

        :param selection: List of selected td.OP instances.
        :type  selection: list of td.OP
        :param data: Properties for creation.
        :type  data: dict
        :param name: Name of the Component.
        :type  name: str
        """
        super(TDGamComponent, self).__init__(name)

        if not selection:

            logging.error("Nothing selected!")

        self.type = "touchdesigner"  # planning ahead for Nuke UI...
        # convert raw selection into useable TDGamComponentUI dict.
        self.selection = self.convert_selection(selection)
        self.parent_op = selection[0].parent()
        self.__setup()

    def __repr__(self):
        return "<TDGamConponent: {name}, {repo_dir}>".format(
            name=self.name,
            repo_dir=self.folder())

    def rip_node_params(self):
        """Convert the current selection into tdgam ParDict.

        :return: the ripped params in dict form.
        :rtype:  dict
        """
        params = []
        for op_dict in self.selection:

            op_dict_as_string = str(op_dict).replace("\"", re.escape("\""))
            op_dict_as_string = op_dict_as_string.replace("'", "\"")
            logging.debug(pformat(op_dict))
            try:
                params.append(json.loads(op_dict_as_string))

            except json.decoder.JSONDecodeError as e:
                logging.exception("FAILED ON {}".format(op_dict["path"]))
                logging.debug(op_dict)

        return params

    def __setup(self):
        """Create necessary directory tree and repo."""
        self.create_json_stash(self.folder(), self.rip_node_params())
        # init git repo for this component's folder
        self.init_repo(self.folder())

    def convert_selection(self, selection):
        """Pull what we need from the original operator instances.

        :return: list of parameter-dicts pulled from the selection
        :rtype:  list
        """
        converted_selection = []
        if self.type == "touchdesigner":
            touch_designer = TouchDesigner()
            converted_selection = touch_designer.convert_to_tdgam_data(
                selection, recurse=True)

        return converted_selection

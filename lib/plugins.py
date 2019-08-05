"""App-specific selection-conversion methods.

can't get this to work yet:
TDJ = td.op.TDModules.mod.TDJSON
"""
import json

from .utilities import td_class_from_string
from .exceptions import TDGamInvalidParameterValue
from .exceptions import GamPluginException

PLUGIN = None
try:
    import td
    TDJ = td.op.TDModules.mod.TDJSON
    PLUGIN = "TouchDesigner"
except ImportError as e:
    print("Only Touchdesigner currently spported!")
    raise

if not PLUGIN:
    raise GamPluginException("No valid plugin detected.")


class TouchDesigner(object):
    """This class controls the conversion of selected ops in Touch Designer."""

    def convert_to_tdgam_data(self, selection, recurse=False):
        """Convert a list of td.OP instances to data dicts.

        :param selection: List of td.OP's to convert.
        :type  selection: list
        :return: list of data dicts containing parameter names and values.
        :rtype:  list
        """
        results = []
        if recurse:
            results = self._recursive_get_op_data(selection)
        else:
            results = self._get_op_data(selection)

        return results

    @staticmethod
    def _get_op_data(selection):
        """Build TDGam-readable json dict from td.OP instance.

        :param selection: List of td.OP's to convert to data dicts.
        :type  selection: list
        :return: list of dicts of jsonified op data.
        :rtype:  list
        """
        import td
        results = []

        if isinstance(selection, td.OP):
            selection = [selection]

        if not selection:
            return results

        for op_ in selection:

            results.append({
                'name': op_.name,
                'path': op_.path,
                'inputs': TouchDesigner.__convert_to_json(op_.inputs) or [],
                'outputs': TouchDesigner.__convert_to_json(op_.outputs) or [],
                'class_name': op_.__class__.__name__,
                'nodeCenter': [op_.nodeCenterX, op_.nodeCenterY],
                'pars': dict(map(
                    lambda x: (x.name, json.dumps(x.val)),
                    op_.pars()))
            })

        return results

    @classmethod
    def _recursive_get_op_data(cls, selection):
        """Build json dict from list of td.OP's and all nested children.

        :param selection: List of td.OP's to convert to data dicts.
        :type selection:  list of td.OP's
        :return: list of dicts of jsonified op data.
        :rtype:  list
        """
        recursables = ["containerCOMP",
                       "baseCOMP",
                       "geometryCOMP",
                       "lightCOMP"]
        converted_selection = []
        for op_ in selection:

            converted_op = cls._get_op_data(op_)[0]

            # if this is a recursable op-type, create the 'children' key, and
            # recursively populate
            if op_.__class__.__name__ in recursables:
                converted_op["children"] = \
                    cls._recursive_get_op_data(op_.children)

            # append this op
            converted_selection.append(converted_op)

        return converted_selection

    @staticmethod
    def __convert_to_json(data):
        """Convert various types to TDGam-readable json.

        :param data: the data to be converted.
        :type  data: *
        :return: the same data with everything properly represented as json.
        :rtype:  *
        """
        import td

        def __convert(item):

            converted_result = None
            # make sure td.OP instances get converted to dicts
            if isinstance(item, td.OP):
                op_repr_dict = {
                    "type": item.__class__.__name__,
                    "path": item.path
                }
                converted_result = op_repr_dict

            else:
                converted_result = json.loads(
                    str(item).replace("'", "\""))

            return converted_result

        converted_data = None

        # lists
        if isinstance(data, list):
            converted_data = []

            for item in data:

                converted_data.append(__convert(item))

        #  dicts
        elif isinstance(data, dict):
            converted_data = {}
            for key, val in data.items():

                converted_data[key] = __convert(val)

        elif isinstance(data, cls):

            converted_data = __convert(data)

        else:
            try:
                converted_data = json.loads(str(data))
            except:
                msg = "\n\tFailed to convert: {}".format(data)
                raise TDGamInvalidParameterValue(msg)

        return converted_data

    def recreate(self, target_op, selection, recurse=False):
        """Recreate a Touch Designer selection from a ParDict.

        :param target_op: the target op to recreate in.
        :type  target_op: td.Op
        :param selection: the selection data to recreate from.
        :type  selection: list
        :param recurse: flag to recursively recreate or just the first level.
        :type  recurse: bool
        :return: list of recreated results
        :rtype: list
        """
        results = []

        if recurse:
            results = self.__recursive_recreate(target_op, selection)

        else:
            results = self._recreate(target_op, selection)

        self.__rebuild_connections(selection)

        return results

    @staticmethod
    def __rebuild_connections(selection):
        """Rebuild the connections of ops from resding the selection ParDict's.

        :param selection: the selection data to recreate the connections from.
        :type  selection: list
        """
        import td

        for op_data in selection:

            op_ = td.op(op_data["path"])
            for i, input_tdpath in enumerate(op_data["inputs"]):

                op_.inputConnectors[i] = td.op(input_tdpath)

            for i, output_tdpath in enumerate(op_data["outputs"]):

                op_.outputConnectors[i] = td.op(output_tdpath)

    @staticmethod
    def _recreate(target_op, selection):
        """Recreate new op from selection-data.

        :param target_op: Parent to create inside.
        :type  target: td.OP
        :param data: Data from the json for this op.
        :type  date: dict of properties originally saved to json.
        :return: A recreation of the original op instance.
        :rtype:  td.Op
        """
        import td
        recreated = []
        if not isinstance(selection, list):
            selection = [selection]

        if not selection:
            return recreated

        for op_data in selection:

            op_class = td_class_from_string(op_data["class_name"])
            op_name = op_data["name"]

            recreated_op = target_op.create(op_class, op_name)
            recreated_op.nodeCenterX, recreated_op.nodeCenterX = \
                op_data["nodeCenter"]
            recreated.append(recreated_op)

        return recreated

    def __recursive_recreate(self, target_op, selection):
        """Recreate new op and nested children-ops from selection-data.

        :param target_op: Parent to create inside.
        :type  target: td.OP
        :param data: Data from the json for this op.
        :type  date: dict of properties originally saved to json.
        :return: A list of recreated op instances.
        :rtype:  list
        """
        import td
        recreated_list = []

        for op_data in selection:

            op_parent_path = "/".join(op_data["path"].split("/")[:-1])
            op_parent = td.op(op_parent_path)  # parent

            recreated_op = self._recreate(op_parent, op_data)[0]  # op

            if op_data.get("children", False):
                self.__recursive_recreate(
                    recreated_op, op_data["children"])
                recreated_list.append(recreated_op)

            else:
                recreated_list.append(recreated_op)

        return recreated_list

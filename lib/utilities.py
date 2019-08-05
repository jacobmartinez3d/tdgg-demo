"""TDGam Tool Bag"""
import logging
from os import makedirs
from os import environ
from os import path as osp

import scandir
import td

from .exceptions import TDGamComponentException

ML_LOG_PATH = osp.join(osp.expanduser("~"), "tdgam_logs")


def logger():
    """retrieve the logger for target project.

    :return: the logging module.
    :rtype:  logging
    """
    if not osp.exists(ML_LOG_PATH):
        makedirs(ML_LOG_PATH)

    project_name = osp.basename(td.project.folder)
    logging.getLogger(project_name)
    logging.basicConfig(filename=osp.join(ML_LOG_PATH, project_name),
                        level=logging.DEBUG)

    return logging


def rscandir(path, ignore_dirs=[]):
    """retrieve flattened list of filepaths in the given diectory-tree.

    :param path: the pat of the directory-tree to scan.
    :type  path: str
    :param ignore_dirs: a list of directories to ignore during recursion.
    :type  ignore_dirs: list
    :return: list of filepaths for every found file in the tree.
    :rtype:  list
    """
    results = []

    for entry in scandir.scandir(path):

        if entry.is_dir() and entry.name not in ignore_dirs:
            results += rscandir(entry.path)

        elif entry.is_file():
            results.append(entry.path)

    return results


def td_class_from_string(class_string):
    """retrieve td op class object from string.

    This is a utility function mainly intended for use in conjunction with the
    td module's "td.op(<op>).create(<td op class>, <name>)" function.

        Example:
        td.op(<op>).create(td_class_from_string('td.hsvtorgbTOP'),
            'my_hsvtorgb_top'))

    :param class_string: the string version of the class to retrieve.
    :type  class_string: str
    :return: the td class for thengiven string.
    :rtype:  Touch Designer class object
    """
    td_classes = vars(td)
    if class_string not in td_classes:
        msg = ("This is not a valid Touch Designer Class, or the"
               "class is not supported yet.")
        raise TDGamComponentException(msg)

    return td_classes.get(class_string, None)


def create_active_op(target_op, class_name, name):
    """Create an op via Touc Designer's API and set it's viewer to active.

    :param target_op: the target op to create the new active op in.
    :type  target_op: td.Op
    :param class_name: the class type to create.
    :type  class_name: str
    :param name: the name of the newn op to create.
    :type  name: str
    :return: the newly created op.
    :rtype:  td.Op
    """
    op_ = target_op.create(td_class_from_string(class_name), name)
    op_.viewer = 1
    op_.activeViewer = 1

    return op_


def tdgamlog(msg, type_, length):
    """Log a message to the terminal in the target type_ and length.

    :param msg: the message to log.
    :type  msg: str
    :param type_: the type of msg to log.
    :type  type_: str
    :param length: amount of characters in the terminal to limit each line to.
    :type  length: int
    """
    primary_divider = "#" * length
    secondary_divider = "_" * length
    tertiary_divider = "-" * length
    msg_str = ""

    if type_.lower() == "info":
        td.ui.status = "[TDGam] " + msg
        msg_str = "\n".join([
            "\n",
            msg])

    elif type_ == "path":
        msg_str = "\n".join([
            tertiary_divider,
            "\tpath :\t" + msg,
            tertiary_divider])

    elif type_ == "results":
        if isinstance(msg, list):
            msg = ["\t-\t" + str(list_item) for list_item in msg]

        msg_str = "\n".join([
            secondary_divider,
            "\n".join(msg),
            secondary_divider])

    elif type_ == "warning":
        td.ui.status = "[TDGam Warning] " + msg
        msg_str = "\n".join([
            primary_divider,
            "\n",
            "\t" + msg,
            "\n",
            primary_divider])

    logger().info(msg_str)

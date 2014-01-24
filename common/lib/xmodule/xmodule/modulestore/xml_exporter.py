"""
Methods for exporting course data to XML
"""

import logging
from xmodule.modulestore import Location
from xmodule.modulestore.inheritance import own_metadata
from fs.osfs import OSFS
from json import dumps
import json
import datetime
import os
import shutil
import filecmp

DRAFT_DIR = "drafts"
PUBLISHED_DIR = "published"

class EdxJSONEncoder(json.JSONEncoder):
    """
    Custom JSONEncoder that handles `Location` and `datetime.datetime` objects.

    `Location`s are encoded as their url string form, and `datetime`s as
    ISO date strings
    """
    def default(self, obj):
        if isinstance(obj, Location):
            return obj.url()
        elif isinstance(obj, datetime.datetime):
            if obj.tzinfo is not None:
                if obj.utcoffset() is None:
                    return obj.isoformat() + 'Z'
                else:
                    return obj.isoformat()
            else:
                return obj.isoformat()
        else:
            return super(EdxJSONEncoder, self).default(obj)


def export_to_xml(modulestore, contentstore, course_location, root_dir, course_dir, draft_modulestore=None):
    """
    Export all modules from `modulestore` and content from `contentstore` as xml to `root_dir`.

    `modulestore`: A `ModuleStore` object that is the source of the modules to export
    `contentstore`: A `ContentStore` object that is the source of the content to export, can be None
    `course_location`: The `Location` of the `CourseModuleDescriptor` to export
    `root_dir`: The directory to write the exported xml to
    `course_dir`: The name of the directory inside `root_dir` to write the course content to
    `draft_modulestore`: An optional `DraftModuleStore` that contains draft content, which will be exported
        alongside the public content in the course.
    """

    course_id = course_location.course_id
    course = modulestore.get_course(course_id)

    fs = OSFS(root_dir)
    export_fs = fs.makeopendir(course_dir)

    xml = course.export_to_xml(export_fs)
    with export_fs.open('course.xml', 'w') as course_xml:
        course_xml.write(xml)

    # export the static assets
    policies_dir = export_fs.makeopendir('policies')
    if contentstore:
        contentstore.export_all_for_course(
            course_location,
            root_dir + '/' + course_dir + '/static/',
            root_dir + '/' + course_dir + '/policies/assets.json',
        )

    # export the static tabs
    export_extra_content(export_fs, modulestore, course_id, course_location, 'static_tab', 'tabs', '.html')

    # export the custom tags
    export_extra_content(export_fs, modulestore, course_id, course_location, 'custom_tag_template', 'custom_tags')

    # export the course updates
    export_extra_content(export_fs, modulestore, course_id, course_location, 'course_info', 'info', '.html')

    # export the 'about' data (e.g. overview, etc.)
    export_extra_content(export_fs, modulestore, course_id, course_location, 'about', 'about', '.html')

    # export the grading policy
    course_run_policy_dir = policies_dir.makeopendir(course.location.name)
    with course_run_policy_dir.open('grading_policy.json', 'w') as grading_policy:
        grading_policy.write(dumps(course.grading_policy, cls=EdxJSONEncoder))

    # export all of the course metadata in policy.json
    with course_run_policy_dir.open('policy.json', 'w') as course_policy:
        policy = {'course/' + course.location.name: own_metadata(course)}
        course_policy.write(dumps(policy, cls=EdxJSONEncoder))

    # export draft content
    # NOTE: this code assumes that verticals are the top most draftable container
    # should we change the application, then this assumption will no longer
    # be valid
    if draft_modulestore is not None:
        draft_verticals = draft_modulestore.get_items([None, course_location.org, course_location.course,
                                                       'vertical', None, 'draft'])
        if len(draft_verticals) > 0:
            draft_course_dir = export_fs.makeopendir(DRAFT_DIR)
            for draft_vertical in draft_verticals:
                parent_locs = draft_modulestore.get_parent_locations(draft_vertical.location, course.location.course_id)
                # Don't try to export orphaned items.
                if len(parent_locs) > 0:
                    logging.debug('parent_locs = {0}'.format(parent_locs))
                    draft_vertical.xml_attributes['parent_sequential_url'] = Location(parent_locs[0]).url()
                    sequential = modulestore.get_item(Location(parent_locs[0]))
                    index = sequential.children.index(draft_vertical.location.url())
                    draft_vertical.xml_attributes['index_in_children_list'] = str(index)
                    draft_vertical.export_to_xml(draft_course_dir)


def export_extra_content(export_fs, modulestore, course_id, course_location, category_type, dirname, file_suffix=''):
    query_loc = Location('i4x', course_location.org, course_location.course, category_type, None)
    items = modulestore.get_items(query_loc, course_id)

    if len(items) > 0:
        item_dir = export_fs.makeopendir(dirname)
        for item in items:
            with item_dir.open(item.location.name + file_suffix, 'w') as item_file:
                item_file.write(item.data.encode('utf8'))


def convert_between_versions(source_dir, target_dir):
    """
    Converts a version 0 export format to version 1, and vice versa.

    @param source_dir: the directory structure with the course export that should be converted.
       The contents of source_dir will not be altered.
    @param target_dir: the directory where the converted export should be written.
    @return: the version number of the converted export.
    """
    def convert_to_version_1():
        """ Convert a version 0 archive to version 0 """
        os.mkdir(copy_root)
        with open(os.path.join(copy_root, 'format.json'), 'w') as f:
            f.write('{"export_format": 1}\n')

        # If a drafts folder exists, copy it over.
        copy_drafts()

        # Now copy everything into the published directory
        published_dir = os.path.join(copy_root, PUBLISHED_DIR)
        shutil.copytree(os.path.join(source_dir, course_name), published_dir)
        # And delete the nested drafts directory, if it exists.
        nested_drafts_dir = os.path.join(published_dir, DRAFT_DIR)
        if os.path.isdir(nested_drafts_dir):
            shutil.rmtree(nested_drafts_dir)

    def convert_to_version_0():
        """ Convert a version 1 archive to version 0 """
        # Copy everything in "published" up to the top level.
        published_dir = os.path.join(source_dir, course_name, PUBLISHED_DIR)
        if not (os.path.isdir(published_dir)):
            raise ValueError("a version 1 archive must contain a published branch")

        shutil.copytree(published_dir, copy_root)

        # If there is a "draft" branch, copy it. All other branches are ignored.
        copy_drafts()

    def copy_drafts():
        """
        Copy drafts directory from the old archive structure to the new.
        """
        draft_dir = os.path.join(source_dir, course_name, DRAFT_DIR)
        if os.path.isdir(draft_dir):
            shutil.copytree(draft_dir, os.path.join(copy_root, DRAFT_DIR))

    root = os.listdir(source_dir)
    if len(root) != 1 or os.path.isfile(os.path.join(source_dir, root[0])):
        raise ValueError("source archive does not have single course directory at top level")

    course_name = root[0]

    # For this version of the script, we simply convert back and forth between version 0 and 1.
    original_version = get_version(os.path.join(source_dir, course_name))
    if original_version not in [0, 1]:
        raise ValueError("unknown version: " + str(original_version))
    desired_version = 1 if original_version is 0 else 0

    copy_root = os.path.join(target_dir, course_name)

    if desired_version == 1:
        convert_to_version_1()
    else:
        convert_to_version_0()

    return desired_version


def get_version(course_directory):
    """
    Return the export format version number for the given
    archive directory structure.

    If the archived file does not correspond to a known export
    format, None will be returned.
    """
    format_file = os.path.join(course_directory, "format.json")
    if not os.path.isfile(format_file):
        return 0
    with open(format_file, "r") as f:
        data = json.load(f)
        if 'export_format' in data:
            return data['export_format']

    return None


def directories_equal(directory1, directory2):
    """
    Returns True if the 2 directories have equal content, else false.
    """
    def compare_dirs(dir1, dir2):
        """ Compare directories for equality. """
        comparison = filecmp.dircmp(dir1, dir2)
        if (len(comparison.left_only) > 0) or (len(comparison.right_only) > 0):
            return False
        if (len(comparison.funny_files) > 0) or (len(comparison.diff_files) > 0):
            return False
        for subdir in comparison.subdirs:
            if not compare_dirs(os.path.join(dir1, subdir), os.path.join(dir2, subdir)):
                return False

        return True

    return compare_dirs(directory1, directory2)

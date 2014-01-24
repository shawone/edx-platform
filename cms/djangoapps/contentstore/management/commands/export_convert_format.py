"""
Script for converting a tar.gz file representing an exported course
to the archive format used by a different version of export.
"""
import os

from django.core.management.base import BaseCommand, CommandError

from tempfile import mkdtemp
import tarfile
import shutil
from extract_tar import safetar_extractall

from xmodule.modulestore.xml_exporter import convert_between_versions


class Command(BaseCommand):
    """
    Convert between export formats.
    """
    help = 'Convert between versions 0 and 1 of the course export format'

    def handle(self, *args, **options):
        "Execute the command"
        if len(args) != 2:
            raise CommandError("export requires two arguments: <tar.gz file> <output path>")

        source_archive = args[0]
        output_path = args[1]

        # Create temp directories to extract the source and create the target archive.
        temp_source_dir = mkdtemp()
        temp_target_dir = mkdtemp()
        try:
            extract_source(source_archive, temp_source_dir)

            desired_version = convert_between_versions(temp_source_dir, temp_target_dir)

            # New zip up the target directory.
            parts = os.path.basename(source_archive).split('.')
            archive_name = os.path.join(output_path, parts[0] + "_version_" + str(desired_version) + ".tar.gz")
            with open(archive_name, "w"):
                tar_file = tarfile.open(archive_name, mode='w:gz')
                try:
                    for item in os.listdir(temp_target_dir):
                        tar_file.add(os.path.join(temp_target_dir, item), arcname=item)

                finally:
                    tar_file.close()

            print("Created archive {0}".format(archive_name))

        except ValueError as err:
            raise CommandError(err)

        finally:
            shutil.rmtree(temp_source_dir)
            shutil.rmtree(temp_target_dir)


def extract_source(source_archive, target):
    """
    Extract the archive into the given target directory.
    """
    tar_file = tarfile.open(source_archive)
    try:
        safetar_extractall(tar_file, target)
    finally:
        tar_file.close()

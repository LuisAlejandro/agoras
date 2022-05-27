# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2016-2022, Social Actions CLI Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

import yamale

from ..core.logger import logger
from ..core.errors import sacliNotFound, SchemaNotFound, ValidationError
from ..core.installer import Installer


def validate(saclipath, schemapath):

    try:
        schema = yamale.make_schema(schemapath, parser='ruamel')
        data = yamale.make_data(saclipath, parser='ruamel')
        yamale.validate(schema, data)
        return data
    except yamale.YamaleError as e:
        for result in e.results:
            logger.error(
                "Error validating data "
                "'%s' with '%s'\n\t" % (result.data, result.schema)
            )
            for error in result.errors:
                raise ValidationError(error)


def main(**kwargs):

    conffile = kwargs.get('conffile')
    currdir = os.getcwd()
    filedir = os.path.dirname(os.path.abspath(__file__))
    basedir = os.path.abspath(os.path.join(filedir, '..'))
    schemadir = os.path.join(basedir, 'config')
    schemapath = os.path.join(schemadir, 'schema.yml')

    if conffile:
        saclipath = os.path.abspath(conffile)
    else:
        saclipath = os.path.join(currdir, '.sacli.yml')

    if not os.path.isfile(saclipath):
        raise sacliNotFound(currdir)

    if not os.path.isfile(schemapath):
        raise SchemaNotFound(schemadir)

    sacli = validate(saclipath, schemapath)

    installer = Installer(sacli)
    # installer.execute()

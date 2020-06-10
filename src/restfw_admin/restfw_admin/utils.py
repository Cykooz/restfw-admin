# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 05.02.2020
"""
import re


# def add_admin_resource(root, key, resource, api_version):
#     """
#     :type root: mountbit.provisioner.rest.root.ProvisionerRoot
#     :type key: str
#     :type resource: restfw.resource.Resource
#     :type api_version: int
#     """
#     root.get_api_root(api_version)['admin_resources'][key] = resource


# def get_admin_resource(root, key, api_version=None):
#     """
#     :type root: mountbit.provisioner.rest.root.ProvisionerRoot
#     :type key: str
#     :type api_version: int or None
#     :rtype: restfw.resource.Resource
#     """
#     return root.get_api_root(api_version)['admin_resources'][key]


# def set_default_admin_resource(root, key, default_resource, api_version):
#     """
#     :type root: mountbit.provisioner.rest.root.ProvisionerRoot
#     :type key: str
#     :type default_resource: restfw.resource.Resource
#     :type api_version: int
#     """
#
#     admin_resources = root.get_api_root(api_version)['admin_resources']
#     if key in admin_resources:
#         return admin_resources[key]
#     admin_resources[key] = default_resource
#     return default_resource


# def add_dynamic_admin_react_resource(config, name, fabric, after=None, before=None):
#     """
#     Add a `factory of admin_react resource`.
#
#     ``fabric`` should be a callable conforming to the
#     :class:`mountbit.provisioner.admin.interfaces.IAdminResourceJsFabric` interface.
#
#     ``name`` should be the name of the resource fabric. There are no
#     restrictions on the name of a resource fabric. If left unspecified, the
#     name will be constructed from the name of the ``resource``.
#
#     The ``after`` and ``before`` options can be used to control the ordering
#     of resource fabrics by providing hints about where in the fabrics list
#     the fabric is used. Each option may be a string or a list of strings.
#     At least one resource fabric in each, the after and before directions, must
#     exist to fully satisfy the constraints.
#
#     ``after`` means closer to the end of list of fabrics,
#     and ``before`` means closer to start of list of fabrics.
#     """
#     if before:
#         before = as_sorted_tuple(before)
#     if after:
#         after = as_sorted_tuple(after)
#
#     discriminator = ('admin_react resource', name)
#     intr = config.introspectable(
#         'admin_react resources',
#         name,
#         name,
#         'admin_react resource'
#     )
#     intr['name'] = name
#     intr['resource_fabric'] = fabric
#     intr['under'] = after
#     intr['over'] = before
#
#     def register():
#         fabrics = config.registry.queryUtility(IAdminResources)
#         if fabrics is None:
#             fabrics = TopologicalSorter()
#             config.registry.registerUtility(fabrics, IAdminResources)
#         fabrics.add(name, fabric, after=after, before=before)
#
#     config.action(discriminator, register, introspectables=(intr,))
#
#
# def add_static_admin_react_resource(config, name, asset_spec, package=None, after=None, before=None):
#     resolver = AssetResolver(package)
#     asset_descriptor = resolver.resolve(asset_spec)
#     path = asset_descriptor.abspath()
#     with open(path, 'rt') as f:
#         js_code = f.read().decode('utf-8')
#     add_dynamic_admin_react_resource(
#         config,
#         name=name,
#         fabric=lambda request: js_code,
#         after=after, before=before,
#     )
#
#
# def get_public_admin_settings(registry):
#     """
#     :type registry: pyramid.registry.Registry
#     :rtype: IPublicAdminSettings
#     """
#     return registry.queryUtility(IPublicAdminSettings)
#
#
# def set_public_admin_settings(registry, name, value):
#     """
#     :type registry: pyramid.registry.Registry
#     :type name: str
#     :type value: str
#     :rtype: IPublicAdminSettings
#     """
#     settings = registry.queryUtility(IPublicAdminSettings)
#     settings[name] = value


FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')


def convert_to_snake_case(name: str):
    tmp = FIRST_CAP_RE.sub(r'\1_\2', name)
    return ALL_CAP_RE.sub(r'\1_\2', tmp).lower()


def slug_to_title(slug: str):
    return ' '.join(n.capitalize() for n in slug.split('_'))

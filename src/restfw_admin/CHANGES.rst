..  Changelog format guide.
    - Before make new release of core egg you MUST add here a header for new version with name "Next release".
    - After all headers and paragraphs you MUST add only ONE empty line.
    - At the end of sentence which describes some changes SHOULD be identifier of task from our task manager.
      This identifier MUST be placed in brackets. If a hot fix has not the task identifier then you
      can use the word "HOTFIX" instead of it.
    - At the end of sentence MUST stand a point.
    - List of changes in the one version MUST be grouped in the next sections:
        - Features
        - Changes
        - Bug Fixes
        - Docs

CHANGELOG
*********

1.4.8 (2025-02-27)
==================

Features
--------

- Added ``FileField`` and ``FileInput`` widgets.
- Added custom implementation of ``IFileUploadProvider``.
- Added support default values for ``InputWidgets``.

1.4 (2024-12-11)
================

Features
--------

- Updated all dependencies.
- ``react-admin`` was updated to version 5.4.2.

Changes
-------

- Set default value of ``ReferenceInput.per_page`` as 500.
- Update ``ChoicesWidget`` to support a list of strings as choices.

Bug Fixes
---------

- Fixed setting page title.

1.3 (2024-07-12)
================

Features
--------

- Updated all dependencies.
- ``react-admin`` was updated to version 5.0.
- Added ``ListViewSettings.infinite_pagination`` setting.

1.2 (2024-02-15)
================

Features
--------

- Added support of requesting resource items by filter ``<id_filed>__in``.
  Such filter is used in internals of ``react-admin``.

Changed
-------

- Updated dependencies.

1.1.2 (2024-02-07)
==================

Bug Fixes
---------

- Fixed request body for DELETE method.

1.1 (2024-01-26)
================

Features
--------

- Added ``UrlField`` widget.

Changed
-------

- Updated dependencies.

1.0 (2023-12-20)
================

Features
--------

- Added support of server-validation.

Changes
-------

- Updated dependencies.

0.14.2 (2023-11-30)
===================

Bug Fixes
---------

- Fixed error with node's widget.

0.14 (2023-11-30)
=================

Changes
-------

- Updated dependencies.

Bug Fixes
---------

- Fixed duplication of ``MinLength`` validator in ``TextInput`` widget.
- Fixed error ``method is null`` when filter contains only one item.

0.13.2 (2023-10-06)
===================

Bug Fixes
---------

- Added copying ``label`` and ``helper_text`` from widget constructed
  by system into widget specified by user through ``widget`` argument
  of colander's node.

0.13 (2023-10-06)
=================

Features
--------

- Added support of field ``widget`` of colander's node.
  Now you can use it to specify only one widget (field or input)
  for node or you can set it as tuple (list, set) of widgets if you need
  to specify both of field and input widgets.

Changes
-------

- Updated dependencies.
- For ``NumberField`` disabled thousands grouping by default.

0.12.2 (2023-07-12)
===================

Bug Fixes
---------

- Added filling of ``help_text`` for input widgets.

0.12 (2023-07-12)
=================

Features
--------

- Added support of ``colander.Decimal`` node type.

0.11 (2023-07-07)
=================

Features
--------

- Added widgets ``DynSelectField`` and ``DynSelectInput`` that
  work with admin choices.

Changes
-------

- Updated dependencies.

0.10.2 (2023-05-29)
===================

Bug Fixes
---------

- Ignore global fields settings during build filter fields for resource admin UI.

0.10 (2023-05-26)
=================

Features
--------

- Added support filters for list view.
- Added support of getting list of resources bigger than
  limit on page size in backend API.

Changes
-------

- Updated dependencies.

0.9.6 (2023-03-29)
==================

Bug Fixes
---------

- Fixed error in setup.py.

0.9.4 (2023-03-29)
==================

Changes
-------

- Updated dependencies.

Bug Fixes
---------

- Fixed ``JsonField`` in view page.

0.9.2 (2023-01-17)
==================

Changes
-------

- Changed visuals of NestedArrayField with single field.

0.9 (2023-01-16)
================

Features
--------

- Updated ``react-admin`` to version 4.
- Implemented simple and comfortable version of ``JsonField`` and
  ``JsonInput``.
- Added field ``ResourceAdmin.order_by`` to control list of resource fields,
  that may be used for sorting.
- Added widget ``SimpleArrayList``.
- Added widget ``NestedArrayList``.

Changes
-------

- Updated all dependencies.
- Changed sorting of resources in left menu.

0.8 (2022-01-14)
================

Features
--------

- Added function ``set_restfw_admin_extra_params`` to add some extra
  parameters into ApiInfo object in JS part of Admin UI.

Changes
-------

- Updated minimal supported version of restfw to 8.0.2.
- Updated python's and Node.js dependencies.

0.7 (2021-10-28)
================

Changes
-------

- Updated minimal supported version of restfw to 8.0b.
- Updated python's and Node.js dependencies.

0.6.6 (2021-10-28)
==================

Changes
-------

- Migrated private PyPi from http://pypi.mountbit.com to https://nx.cloudike.com.

0.6.4 (2021-07-13)
==================

Changes
-------

- Replaced using of deprecated ``restfw.schemas.MappingSchema`` on
  ``restfw.schemas.MappingNode``.

0.6.2 (2021-07-13)
==================

Changes
-------

- Added support of ``pyramid 2+``.

0.6 (2021-07-05)
================

Features
--------

- Added basic version of ``JsonField`` and ``JsonInput``.

Changes
-------

- Updated dependencies.

0.5.2 (2021-01-25)
==================

Bug Fixes
---------

- Disabled sorting in ``ListView`` and ``ReferenceInput``.

0.5 (2021-01-25)
================

Features
--------

- Migrated to version 6 of ``restfw``.

Changes
-------

- Updated dependencies.

0.4.2 (2020-10-15)
==================

Bug Fixes
---------

- Fixed converting of ``LaconicNoneOf`` validator.

0.4 (2020-10-07)
================

Changes
-------

- Added some CSS-styles for ``MappingField`` and ``MappingInput``.
- Updated dependencies.

Bug Fixes
---------

- Fixed converters for ``SequenceNode``.

0.3 (2020-08-19)
================

Features
--------

- Added basic implementation of ``MappingField`` and ``MappingInput``.

0.2.2 (2020-08-06)
==================

Bug Fixes
---------

- Fixed errors with nullable schema nodes.

0.2 (2020-08-06)
================

Features
--------

- Added ``RichTextField`` and ``RichTextInput`` widgets.

0.1.2 (2020-08-06)
==================

Bug Fixes
---------

- Fixed error with getting of ``Admin`` resource with non default ``prefix``.

0.1 (2020-08-06)
================

Features
--------

- Initial release.

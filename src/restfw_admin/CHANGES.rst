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

"""
:Authors: cykooz
:Date: 14.01.2021
"""

from dataclasses import asdict

from restfw import views
from restfw.interfaces import MethodOptions

from . import schemas
from .resources import Doc, Docs, File


# Doc


@views.resource_view_config(Doc)
class DocView(views.HalResourceView):
    resource: Doc
    options_for_get = MethodOptions(None, schemas.DocSchema, permission='docs.get')
    options_for_patch = MethodOptions(
        schemas.PatchDocSchema,
        schemas.DocSchema,
        permission='docs.edit',
    )
    options_for_delete = MethodOptions(None, None, permission='docs.edit')

    def as_dict(self):
        res = asdict(self.resource.model)
        if res['image'] is None:
            res['image'] = asdict(File())
        return res


# Docs


@views.resource_view_config(Docs)
class DocsView(views.HalResourceWithEmbeddedView):
    resource: Docs
    options_for_get = MethodOptions(
        schemas.GetDocsSchema,
        schemas.DocsSchema,
        permission='docs.get',
    )
    options_for_post = MethodOptions(
        schemas.CreateDocSchema,
        schemas.DocSchema,
        permission='docs.edit',
    )

    def get_embedded(self, params):
        name = params.get('name')
        docs = [
            self.resource.get_doc_by_model(model)
            for model in self.resource.models.values()
            if not name or model.name == name
        ]
        return views.list_to_embedded_resources(
            self.request,
            params,
            docs,
            parent=self.resource,
            embedded_name='docs',
        )

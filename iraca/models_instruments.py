from iraca import models, forms

models = {
    'documento_1':{
            'model':models.Documento,
            'form':forms.DocumentoForm,
            'template':'iraca/implementation/activities/instruments/templates/documento.html',
            'template_view':'iraca/implementation/activities/instruments/templates/documento_ver.html'
        },
}

def get_model(key):
    return models[key]
from iraca import models, forms

models = {
    'documento_1':{
            'model':models.Documento,
            'form':forms.DocumentoHogarForm,
            'template':'iraca/individual/territorios/comunity/ruta/hogares/momento/templates/documento.html',
            'template_view':'iraca/individual/territorios/comunity/ruta/hogares/momento/templates/documento_ver.html',
            'template_support':'iraca/implementation/activities/instruments/templates/documento_support.html'
        },
}

def get_model(key):
    return models[key]
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            1MB - 1048576
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 52428800
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    """
    def __init__(self, *args, **kwargs):
        try:
            self.content_types = kwargs.pop("content_types")
        except KeyError:
            self.content_types = None

        try:
            self.max_upload_size = kwargs.pop("max_upload_size")
        except KeyError:
            self.max_upload_size = None

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)

        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('El archivo debe ser maximo de %s. El archivo seleccionado tiene %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('Formato no permitido.'))
        except AttributeError:
            pass

        return data


class PDFFileField(ContentTypeRestrictedFileField):
    '''
    Validates that the file is a PDF
    '''
    def __init__(self, *args, **kwargs):
        super(PDFFileField, self).__init__(content_types = ['application/pdf'], *args, **kwargs)

    def clean(self, *args, **kwargs):
        from PyPDF2 import PdfFileReader
        data = super(PDFFileField, self).clean(*args, **kwargs)

        file = data.file

        try:
            PdfFileReader(file)
        except Exception as e:
            raise forms.ValidationError(_('El archivo no es un PDF'))

        return data
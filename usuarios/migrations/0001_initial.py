# Generated by Django 2.0.1 on 2018-02-13 16:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import config.extrafields
import usuarios.models
import uuid
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from usuarios.models import ContentTypeSican

def create_permissions(apps, schema_editor):

    content_type = ContentType.objects.get_for_model(ContentTypeSican)

    db_alias = schema_editor.connection.alias

    Permission.objects.using(db_alias).bulk_create([
        Permission(name="Usuarios, ver aplicación", content_type = content_type, codename = 'usuarios.ver'),

        Permission(name="Usuarios, ver cuentas", content_type=content_type, codename='usuarios.cuentas.ver'),
        Permission(name="Usuarios, ver roles", content_type=content_type, codename='usuarios.roles.ver'),
        Permission(name="Usuarios, ver permisos", content_type=content_type, codename='usuarios.permisos.ver'),
        Permission(name="Usuarios, ver codigos", content_type=content_type, codename='usuarios.codigos.ver'),

        Permission(name="Usuarios, crear cuentas", content_type=content_type, codename='usuarios.cuentas.crear'),
        Permission(name="Usuarios, crear roles", content_type=content_type, codename='usuarios.roles.crear'),
        Permission(name="Usuarios, crear permisos", content_type=content_type, codename='usuarios.permisos.crear'),
        Permission(name="Usuarios, crear codigos", content_type=content_type, codename='usuarios.codigos.crear'),

        Permission(name="Usuarios, editar cuentas", content_type=content_type, codename='usuarios.cuentas.editar'),
        Permission(name="Usuarios, editar roles", content_type=content_type, codename='usuarios.roles.editar'),
        Permission(name="Usuarios, editar permisos", content_type=content_type, codename='usuarios.permisos.editar'),
        Permission(name="Usuarios, editar codigos", content_type=content_type, codename='usuarios.codigos.editar'),

        Permission(name="Usuarios, eliminar cuentas", content_type=content_type, codename='usuarios.cuentas.eliminar'),
        Permission(name="Usuarios, eliminar roles", content_type=content_type, codename='usuarios.roles.eliminar'),
        Permission(name="Usuarios, eliminar permisos", content_type=content_type, codename='usuarios.permisos.eliminar'),
        Permission(name="Usuarios, eliminar codigos", content_type=content_type, codename='usuarios.codigos.eliminar')
    ])

def create_groups(apps, schema_editor):

    #Consulta de cuentas
    consulta_cuentas, created = Group.objects.get_or_create(name = 'Usuarios, consulta cuentas')
    permisos_consulta_cuentas = Permission.objects.filter(codename__in = [
        'usuarios.ver',
        'usuarios.cuentas.ver'
    ])
    consulta_cuentas.permissions.add(*permisos_consulta_cuentas)

    #Edicion de cuentas
    edicion_cuentas, created = Group.objects.get_or_create(name='Usuarios, edición cuentas')
    permisos_edicion_cuentas = Permission.objects.filter(codename__in=[
        'usuarios.ver',
        'usuarios.cuentas.ver',
        'usuarios.cuentas.crear',
        'usuarios.cuentas.editar',
        'usuarios.cuentas.eliminar'
    ])
    edicion_cuentas.permissions.add(*permisos_edicion_cuentas)


    # Consulta de roles
    consulta_roles, created = Group.objects.get_or_create(name='Usuarios, consulta roles')
    permisos_consulta_roles = Permission.objects.filter(codename__in=[
        'usuarios.ver',
        'usuarios.roles.ver'
    ])
    consulta_roles.permissions.add(*permisos_consulta_roles)

    # Edicion de roles
    edicion_roles, created = Group.objects.get_or_create(name='Usuarios, edición roles')
    permisos_edicion_roles = Permission.objects.filter(codename__in=[
        'usuarios.ver',
        'usuarios.roles.ver',
        'usuarios.roles.crear',
        'usuarios.roles.editar',
        'usuarios.roles.eliminar'
    ])
    edicion_roles.permissions.add(*permisos_edicion_roles)




    # Consulta de roles
    permisos_permisos, created = Group.objects.get_or_create(name='Usuarios, consulta permisos')
    permisos_consulta_permisos = Permission.objects.filter(codename__in=[
        'usuarios.ver',
        'usuarios.permisos.ver'
    ])
    permisos_permisos.permissions.add(*permisos_consulta_permisos)

    # Edicion de roles
    edicion_permisos, created = Group.objects.get_or_create(name='Usuarios, edición permisos')
    permisos_edicion_permisos = Permission.objects.filter(codename__in=[
        'usuarios.ver',
        'usuarios.permisos.ver',
        'usuarios.permisos.crear',
        'usuarios.permisos.editar',
        'usuarios.permisos.eliminar'
    ])
    edicion_permisos.permissions.add(*permisos_edicion_permisos)



    # Consulta de codigos
    permisos_codigos, created = Group.objects.get_or_create(name='Usuarios, consulta códigos')
    permisos_consulta_codigos = Permission.objects.filter(codename__in=[
        'usuarios.ver',
        'usuarios.codigos.ver'
    ])
    permisos_codigos.permissions.add(*permisos_consulta_codigos)

    # Edicion de codigos
    edicion_codigos, created = Group.objects.get_or_create(name='Usuarios, edición códigos')
    permisos_edicion_codigos = Permission.objects.filter(codename__in=[
        'usuarios.ver',
        'usuarios.codigos.ver',
        'usuarios.codigos.crear',
        'usuarios.codigos.editar',
        'usuarios.codigos.eliminar'
    ])
    edicion_codigos.permissions.add(*permisos_edicion_codigos)



class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('cedula', models.BigIntegerField(unique=True)),
                ('celular', phonenumber_field.modelfields.PhoneNumberField(max_length=128)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('photo', config.extrafields.ContentTypeRestrictedFileField(blank=True, null=True, upload_to=usuarios.models.upload_dinamic_dir)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('notifications', models.IntegerField(default=0)),
                ('messages', models.IntegerField(default=0)),
                ('tipo_sangre', models.CharField(blank=True, max_length=100, null=True)),
                ('last_online', models.DateTimeField(blank=True, null=True)),
                ('is_online', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['first_name'],
            },
        ),
        migrations.CreateModel(
            name='ContentTypeSican',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'sican',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('read', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=100)),
                ('short_description', models.CharField(max_length=500)),
                ('body', models.TextField(max_length=2000)),
                ('date', models.DateTimeField(auto_now=True)),
                ('icon', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),

        migrations.RunPython(create_permissions),
        migrations.RunPython(create_groups)
    ]

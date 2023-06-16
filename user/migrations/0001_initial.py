# Generated by Django 4.2.1 on 2023-06-16 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='이메일')),
                ('nickname', models.CharField(max_length=50, verbose_name='닉네임')),
                ('profile_image', models.CharField(blank=True, max_length=255, null=True, verbose_name='프로필_이미지')),
                ('password', models.CharField(max_length=256, verbose_name='비밀번호')),
                ('sns_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='sns고유번호')),
                ('access_token', models.CharField(blank=True, max_length=255, null=True, verbose_name='접근토큰')),
                ('expires_in', models.CharField(blank=True, max_length=255, null=True, verbose_name='접근토큰_만료시간')),
                ('refresh_token', models.CharField(blank=True, max_length=255, null=True, verbose_name='갱신토큰')),
                ('refresh_token_expires_in', models.CharField(blank=True, max_length=255, null=True, verbose_name='갱신토큰_만료시간')),
                ('age', models.PositiveIntegerField(null=True, verbose_name='나이')),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female')], max_length=1, null=True, verbose_name='성별')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성시각')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정시각')),
                ('login_type', models.CharField(choices=[('normal', '일반'), ('kakao', '카카오'), ('google', '구글'), ('naver', '네이버')], default='normal', max_length=10, verbose_name='로그인유형')),
                ('is_active', models.BooleanField(default=True, verbose_name='활성화여부')),
                ('is_admin', models.BooleanField(default=False, verbose_name='관리자여부')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

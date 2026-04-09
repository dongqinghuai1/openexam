from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_menu_unique_name_per_parent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='标题')),
                ('content', models.TextField(verbose_name='内容')),
                ('level', models.CharField(choices=[('info', '普通'), ('warning', '提醒'), ('urgent', '紧急')], default='info', max_length=20, verbose_name='级别')),
                ('target_type', models.CharField(choices=[('all', '全体'), ('teacher', '教师'), ('student', '学生'), ('parent', '家长'), ('admin', '管理员')], default='all', max_length=20, verbose_name='发送对象')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('published', '已发布')], default='draft', max_length=20, verbose_name='状态')),
                ('published_at', models.DateTimeField(blank=True, null=True, verbose_name='发布时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_notifications', to='users.user', verbose_name='创建人')),
            ],
            options={
                'db_table': 'tb_notification',
                'verbose_name': '通知消息',
                'verbose_name_plural': '通知消息',
                'ordering': ['-created_at'],
            },
        ),
    ]

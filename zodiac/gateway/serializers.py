# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from django_celery_results.models import TaskResult

from .models import *


class TaskResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskResult
        fields = '__all__'


class RequestLogSerializer(serializers.ModelSerializer):
    task_result = TaskResultSerializer()

    class Meta:
        model = RequestLog
        fields = ('id', 'status_code', 'request_url', 'async_result_id',
                  'created_time', 'service', 'task_result')


class ServiceRegistrySerializer(serializers.ModelSerializer):
    results = RequestLogSerializer(source='requestlog', many=True)

    class Meta:
        model = ServiceRegistry
        fields = ('id', 'name', 'description', 'external_uri', 'service_route',
                  'plugin', 'is_active', 'is_private', 'has_active_task', 'method',
                  'application', 'callback_service', 'post_service', 'sources',
                  'created_time', 'modified_time', 'results')

from django_celery_results.models import TaskResult
from rest_framework import serializers

from .models import RequestLog, ServiceRegistry


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
    results = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRegistry
        fields = ('id', 'name', 'description', 'external_uri', 'service_route',
                  'plugin', 'is_active', 'is_private', 'has_active_task',
                  'has_external_trigger', 'method', 'application', 'sources',
                  'created_time', 'modified_time', 'results')

    def get_results(self, obj):
        data = []
        for res in obj.requestlog.all().order_by('-task_result__date_done')[:5]:
            serializer = RequestLogSerializer(res)
            data.append(serializer.data)
        return data

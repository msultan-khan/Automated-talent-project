from rest_framework import serializers


class StartJobSerializer(serializers.Serializer):
    role = serializers.CharField(max_length=120)
    location = serializers.CharField(max_length=120)
    keywords = serializers.CharField(max_length=300)
    job_type = serializers.ChoiceField(choices=["remote", "onsite", "hybrid"])
    search_scope = serializers.ChoiceField(
        choices=["candidates", "projects"], required=False, default="candidates"
    )


class RunJobSerializer(serializers.Serializer):
    job_id = serializers.UUIDField()

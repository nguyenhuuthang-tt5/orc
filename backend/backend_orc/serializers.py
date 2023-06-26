from rest_framework import serializers

class ImageSerializer(serializers.Serializer):
    imageFile = serializers.FileField(required=True)
    #
    def update(self, instance, validated_data):
        pass
    #
    def create(self, validated_data):
        pass

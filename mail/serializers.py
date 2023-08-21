from rest_framework import serializers

from attachment.serializers import AttachmentSerializer
from mail.models import Mail
from user.serializers import UserPublicSerializer
from vendor.serializers import VendorSerializerForInfo


class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mail
        fields = ('id',
                  'type',
                  'title',
                  'order_num',
                  'template',
                  'text',
                  'to_email',
                  'bcc',
                  'cc',
                  'from_email',
                  'from_user',
                  'is_active',
                  'created_at',
                  'attachments',
                  'vendor',
                  'customer'
                  )

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation['attachments'] = AttachmentSerializer(obj.attachments, many=True).data \
            if obj.attachments.count() > 0 else []
        representation['vendor'] = VendorSerializerForInfo(obj.vendor).data if obj.vendor else None
        representation['customer'] = UserPublicSerializer(obj.customer).data if obj.customer else None
        return representation

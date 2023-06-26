from django.conf import settings
from django.http import HttpResponse
from numpy import empty
from rest_framework import generics, status
from rest_framework.response import Response
from backend_orc.serializers import ImageSerializer
from rest_framework.decorators import api_view
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from read_img.read_img import read_image
import os

# config error type 
RS_OK = (0, 'OK')
RS_TYPEFILE_INVALID = (400, 'error.invalid_typefile')
RS_REQUEST_ERROR_EXECUTE = (500, 'error.error_execute')
#
def create_response(rs_code=RS_OK, data=None):
    return Response(status=status.HTTP_200_OK, data={
        'code': rs_code[0],
        'message': rs_code[1]
    })
#
class UploadImage(generics.CreateAPIView):
    serializer_class = ImageSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data= request.FILES)
        if not serializer.is_valid():
            return Response(data={
                'result': 'bad'
            })
        req_data = serializer.validated_data
        imageFile = (req_data['imageFile'])
        path_image_file = f'./file_input/{imageFile}'
        imagePath = default_storage.save(path_image_file, ContentFile(imageFile.read()))
        name, extension = os.path.splitext(imagePath)
        #
        if(extension != '.jpg' and extension != '.png' and extension != '.jpeg'):
            os.remove(path_image_file)
            return create_response(rs_code=RS_TYPEFILE_INVALID)
        # execute core
        resultContent = read_image(image_src=imagePath)
        
        # if failed execute
        errors = list()
        for k, v in resultContent.items():
            if type(v) == str and v == '': 
                errors.append(k + ' ' + 'NotFound')
            if type(v) == list and v == []: 
                errors.append(k + ' ' + 'NotFound')

        return Response(data={
            'result': resultContent,
            'errors': errors
        })

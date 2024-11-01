from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CourseSerializer
from .course_optimizer import main


class OptimizeLearningObjects(APIView):

    def get(self, request):
        serial = CourseSerializer(data=request.GET)

        serial.is_valid(raise_exception=True)

        final_los = main(selected_los=serial.validated_data['learning_object_ids'], time_limit=serial.validated_data['total_time'])

        return Response(final_los)

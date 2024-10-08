from collections import defaultdict
import json
import os
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound

from .metastore import get_all_notebook_meta

from .consts import UNIT_MAPPING

from .models import Course, LearningObject
from .serializers import CellDataSerializer, CourseSerializer, LearningObjectSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class LearningObjectViewSet(viewsets.ModelViewSet):
    queryset = LearningObject.objects.all()
    serializer_class = LearningObjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LearningObject.objects.filter(course__user=self.request.user)


class UpdateLearningObjectsView(APIView):
    def put(self, request):
        data = request.data
        response_data = []

        for lo_data in data:
            try:
                lo = LearningObject.objects.get(id=lo_data['id'])
                serializer = LearningObjectSerializer(lo, data=lo_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response_data.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except LearningObject.DoesNotExist:
                return Response(f"LearningObject with id {lo_data['id']} does not exist", 
                                status=status.HTTP_404_NOT_FOUND)

        return Response(response_data, status=status.HTTP_200_OK)

class AvailableLearningOutcomes(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        notebook_data = get_all_notebook_meta()

        available_los = defaultdict(lambda: defaultdict(list))

        for unit_name, unit_topics in UNIT_MAPPING.items():

            for topic in unit_topics:
                try:
                    topic_metadata = notebook_data[topic]

                    available_los[unit_name][topic] = topic_metadata
                except KeyError as e:
                    print(
                        f"Metadata not found for topic {topic_metadata}. Exception {e}"
                    )
                    continue

        return Response(available_los)


class CellData(APIView):

    def get(self, request, cell_id):
        # TODO: Check if interactive. If interactive, redirect to voila

        htmlFile = cell_id + ".html"
        html_directory = "../voila"
        html_file_path = os.path.join(html_directory, htmlFile)
        try:
            with open(html_file_path) as f:
                content = f.read()
                serializer = CellDataSerializer({'content': content})
                return Response(serializer.data)
        except FileNotFoundError:
            return NotFound("Learning Outcome not found")

        return htmlFile

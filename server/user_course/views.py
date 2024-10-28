from collections import defaultdict
import logging
import os
import re
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, server_error, APIException

from .metastore import get_all_cells, get_all_notebook_meta

from .consts import UNIT_MAPPING

from .models import (
    AIInteraction,
    ActivityLog,
    AssignmentSubmission,
    Course,
    LearningObject,
)
from .serializers import (
    AIInteractionSerializer,
    ActivityLogSerializer,
    AssignmentSubmissionSerializer,
    CellDataSerializer,
    CourseSerializer,
    LearningObjectSerializer,
)
from django.conf import settings
from django.http import FileResponse, HttpResponse, Http404


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


class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer

    def get_queryset(self):
        return AssignmentSubmission.objects.filter(student=self.request.user)


class AIInteractionViewSet(viewsets.ModelViewSet):
    queryset = AIInteraction.objects.all()
    serializer_class = AIInteractionSerializer

    def get_queryset(self):
        return AIInteraction.objects.filter(student=self.request.user)


class UpdateLearningObjectsView(APIView):
    def put(self, request):
        data = request.data
        response_data = []

        for lo_data in data:
            try:
                lo = LearningObject.objects.get(id=lo_data["id"])
                serializer = LearningObjectSerializer(lo, data=lo_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response_data.append(serializer.data)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            except LearningObject.DoesNotExist:
                return Response(
                    f"LearningObject with id {lo_data['id']} does not exist",
                    status=status.HTTP_404_NOT_FOUND,
                )

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
    html_directory = "../voila/out"

    def send_html_file(self, cell_id, quiz_cell=None):
        htmlFile = cell_id + ".html"
        html_file_path = os.path.join(self.html_directory, htmlFile)
        try:
            with open(html_file_path) as f:
                content = f.read()
                serializer = CellDataSerializer(
                    {"content": content, "quiz_cell": quiz_cell}
                )
                return Response(serializer.data)
        except FileNotFoundError:
            logging.error(f"CellID File path not found {html_file_path}")
            raise NotFound("Learning Outcome not found")

    def redirect_to_voila(self, cell_id, anchor=None):
        voila_host = "http://localhost:8866/"
        voila_url = voila_host + f"voila/render/out/{cell_id}.ipynb"

        if anchor:
            voila_url += "#" + anchor

        serializer = CellDataSerializer(
            {"redirect_link": voila_url, "interactive": True}
        )
        return Response(serializer.data)

    def extract_final_quiz_notebook_name(self, text):
        pattern = r"filename:\s*(\w+\.ipynb)"
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None

    def check_final_quiz(self, cell_id):
        module = cell_id.split("-")[0]
        informationCell = module + "-finalQuiz-information"
        htmlFile = informationCell + ".html"
        html_file_path = os.path.join(self.html_directory, htmlFile)

        try:
            with open(html_file_path) as f:
                content = f.read()
                # notebook = self.extract_final_quiz_notebook_name(content)
                # if not notebook:
                #     logging.error(f"Could not find final quiz '{notebook}'")
                #     raise NotFound("Could not find the final quiz notebook")
                # # return self.redirect_to_voila(notebook.split('.')[0])
                # return self.send_html_file(notebook.split('.')[0])
                return self.send_html_file(
                    informationCell, informationCell + "_final_quiz"
                )
        except FileNotFoundError:
            logging.error(f"final quiz File path not found {html_file_path}")
            raise NotFound("Learning Outcome not found")

    def get(self, request, cell_id: str):
        try:
            # TODO: Better check for if interactive.
            if cell_id.startswith("m12-"):
                return self.redirect_to_voila("m12", cell_id)
            elif "-final" in cell_id.lower():
                return self.check_final_quiz(cell_id)
            elif "interactive" in cell_id.lower():
                return self.redirect_to_voila(cell_id)
            else:
                return self.send_html_file(cell_id)
        except Exception as e:
            if isinstance(e, APIException):
                raise e
            return server_error(request)


class MetaDataView(APIView):

    def get(self, request):
        return Response(get_all_cells())


class FileDownloadAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Optional: remove if you want public access
    html_directory = "../voila/out"
    
    def get(self, request, cell_id):
        """
        Download a file from the server.
        """
        try:
            # Define your file storage path
            file_path = os.path.join(self.html_directory, cell_id+".ipynb")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logging.error(f"Quiz file not found - {file_path}")
                return Response(
                    {"error": "File not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Open the file in binary mode
            file = open(file_path, 'rb')
            
            # Create the response
            response = FileResponse(file)
            
            # Set content type and disposition
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment; filename="{cell_id}.ipynb"'
            
            return response
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
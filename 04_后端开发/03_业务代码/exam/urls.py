from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, PaperViewSet, ExamViewSet, ScoreRecordViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'papers', PaperViewSet, basename='paper')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'scores', ScoreRecordViewSet, basename='score')

urlpatterns = [
    path('', include(router.urls)),
]
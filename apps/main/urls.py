from django.urls import path
from .views import TelegramUserView, InformationView, UserView, CheckSubscriberView, RateView, \
    BuySubscriberView, PaymentTypeView, about_view, themes_view, quiz_view, results_view, quiz_answer_view, \
    result_detail_view, questions_check_view, FeedbackView, quiz_content_view

urlpatterns = [
    path("", TelegramUserView.as_view()),
    path("information/", InformationView.as_view()),
    path("questions-check/<int:pk>/", questions_check_view),
    path("about/", about_view),
    path("feedback/<int:pk>/", FeedbackView.as_view()),
    path("user/<int:pk>/", UserView.as_view()),
    path("check/<int:pk>/", CheckSubscriberView.as_view()),
    path("rates/", RateView.as_view()),
    path("payment-types/", PaymentTypeView.as_view()),
    path("themes/<int:pk>/", themes_view),
    path("results/<int:pk>/", results_view),
    path("result-detail/<int:pk>/", result_detail_view),
    path("quiz/<int:pk>/", quiz_view),
    path("quiz-content/<int:pk>/", quiz_content_view),
    path("quiz-answers/<int:pk>/", quiz_answer_view),
    path("buy/<int:pk>/", BuySubscriberView.as_view()),
]

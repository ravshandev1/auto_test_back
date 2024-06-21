from datetime import date, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, response, views
from .models import TelegramUser, Information, About, Subscription, Rate, PaymentType, Theme, Question, Quiz, \
    QuizAnswer, Payment
from .serializers import TelegramUserSerializer, InformationSerializer, RateSerializer, PaymentTypeSerializer
from django.conf import settings
import json
import requests


def themes_view(req, pk):
    lang = req.GET.get('lang')
    qs = Theme.objects.order_by('id')
    data = list()
    title = None
    if lang == "uz":
        title = "Мавзулар"
        for i in qs:
            d = dict()
            d['name'] = i.name_uz
            d['id'] = i.id
            d['count'] = i.questions.all().count()
            data.append(d)
    elif lang == "ru":
        title = "Темы"
        for i in qs:
            d = dict()
            d['name'] = i.name_ru
            d['id'] = i.id
            d['count'] = i.questions.all().count()
            data.append(d)
    return render(req, 'themes.html', context={'title': title, 'themes': data, 'user': pk, 'lang': lang})


def results_view(req, pk):
    user = TelegramUser.objects.filter(telegram_id=pk).first()
    theme_id = req.GET.get('theme_id')
    theme = Theme.objects.filter(id=theme_id).first()
    lang = req.GET.get('lang')
    mes = None
    quizzes = None
    theme_name = None
    theme_count = None
    start_btn = None
    result_btn_name = None
    if lang == 'uz':
        theme_name = theme.name_uz
        theme_count = f"Жами саволлар сони: {theme.questions.all().count()}"
        mes = "Сиз ҳозирча биронта ҳам тест ишламагансиз."
        start_btn = "Тестни бошлаш"
        result_btn_name = "Тўлиқ кўриш"
        theme = "💡 Мавзу:"
        quizzes = list()
        quiz_qs = Quiz.objects.filter(user_id=user.id, theme_id=theme_id)
        for q in quiz_qs:
            d = dict()
            d['quiz_id'] = q.id
            d['id'] = f"ID{q.id} тест натижалари"
            d['theme_name'] = q.theme.name_uz
            d['created_at'] = q.created_at.strftime('%Y-%m-%d %H:%M:%S')
            d['count'] = q.result_count
            d['percentage'] = q.result_percentage
            d['correct_answers_name'] = "🔑 Тўғри жавоб берилган:"
            d['correct_answers_count'] = f"{q.result_count} саволдан ({q.result_percentage})"
            quizzes.append(d)
    elif lang == 'ru':
        theme_name = theme.name_ru
        theme_count = f"Общее количество вопросов: {theme.questions.all().count()}"
        mes = "Вы еще не запустили ни одного теста."
        start_btn = "Запуск теста"
        result_btn_name = "Полный обзор"
        theme = "💡 Тема:"
        quizzes = list()
        quiz_qs = Quiz.objects.filter(user_id=user.id, theme_id=theme_id)
        for q in quiz_qs:
            d = dict()
            d['quiz_id'] = q.id
            d['id'] = f"ID{q.id} результаты теста"
            d['theme_name'] = q.theme.name_ru
            d['created_at'] = q.created_at.strftime('%Y-%m-%d %H:%M:%S')
            d['count'] = q.result_count
            d['percentage'] = q.result_percentage
            d['correct_answers_name'] = "🔑 Правильный ответ:"
            d['correct_answers_count'] = f"{q.result_count} из вопроса ({q.result_percentage})"
            quizzes.append(d)
    ctx = {
        'mes': mes,
        'quizzes': quizzes,
        'user': pk,
        'lang': lang,
        'theme_id': theme_id,
        'theme': theme,
        'theme_name': theme_name,
        'theme_count': theme_count,
        'start_btn_name': start_btn,
        'result_btn_name': result_btn_name
    }
    return render(req, 'results.html', context=ctx)


def questions_check_view(req, pk):
    theme = Theme.objects.filter(id=pk).first()
    qs = theme.questions.all()[:1]
    if len(qs) == 0:
        return JsonResponse({'mes': 'Mes'}, status=400)
    return JsonResponse({'mes': 'Mes'}, status=200)


def quiz_view(req, pk):
    lang = req.GET.get('lang')
    # num = int(req.GET.get('num'))
    theme = Theme.objects.filter(id=pk).first()
    theme_name = None
    question_name = None
    answers = None
    question_count = range(1, theme.questions.all().count() + 1)
    # qs = theme.questions.all()[num - 1:num]
    qs = theme.questions.all()[:1]
    question = qs[0]
    if lang == 'uz':
        theme_name = theme.name_uz
        question_name = question.text_uz
        answers = list()
        for i in question.answers.order_by('id'):
            d = dict()
            d["id"] = i.id
            d["name"] = i.text_uz
            d["is_correct"] = 1 if i.is_correct else 0
            answers.append(d)
    elif lang == 'ru':
        theme_name = theme.name_ru
        question_name = question.text_ru
        answers = list()
        for i in question.answers.order_by('id'):
            d = dict()
            d["id"] = i.id
            d["name"] = i.text_ru
            d["is_correct"] = 1 if i.is_correct else 0
            answers.append(d)
    ctx = {
        'theme_name': theme_name,
        'question_count': question_count,
        'qs_count': theme.questions.all().count(),
        'question': {'name': question_name, 'id': question.id,
                     'image': question.image_path if question.image_path else 0},
        'answers': answers,
        'user': req.GET.get('user'),
        'lang': lang,
        'theme_id': pk,
        'num': 1
    }
    return render(req, 'quiz.html', context=ctx)


def quiz_content_view(req, pk):
    lang = req.GET.get('lang')
    num = int(req.GET.get('num'))
    theme = Theme.objects.filter(id=pk).first()
    question_name = None
    answers = None
    qs = theme.questions.all()[num - 1:num]
    question = qs[0]
    if lang == 'uz':
        question_name = question.text_uz
        answers = list()
        for i in question.answers.order_by('id'):
            d = dict()
            d["id"] = i.id
            d["name"] = i.text_uz
            d["is_correct"] = 1 if i.is_correct else 0
            answers.append(d)
    elif lang == 'ru':
        question_name = question.text_ru
        answers = list()
        for i in question.answers.order_by('id'):
            d = dict()
            d["id"] = i.id
            d["name"] = i.text_ru
            d["is_correct"] = 1 if i.is_correct else 0
            answers.append(d)
    ctx = {
        'question': {'name': question_name, 'id': question.id,
                     'image': question.image_path if question.image_path else 0},
        'answers': answers,
    }
    # print(ctx)
    return JsonResponse(ctx, status=200)


def quiz_answer_view(req, pk):
    user = TelegramUser.objects.filter(telegram_id=pk).first()
    theme_id = req.GET.get('theme_id')
    lang = req.GET.get('lang')
    quiz = Quiz.objects.create(user_id=user.id, theme_id=theme_id)
    try:
        answers = json.loads(req.body).get('quiz')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    for answer in answers:
        QuizAnswer.objects.create(quiz_id=quiz.id, answer_id=answer['answer']['id'], question_id=answer['question']['id'],
                                  is_correct=True if answer['answer']['is_correct'] == 1 else False)
    return JsonResponse({'url': f"/api/v1/result-detail/{quiz.id}/?lang={lang}&theme_id={theme_id}"}, status=200)


def result_detail_view(req, pk):
    theme_id = req.GET.get('theme_id')
    lang = req.GET.get('lang')
    quiz = Quiz.objects.filter(id=pk).first()
    theme = Theme.objects.filter(id=theme_id).first()
    theme_name = None
    quiz_id = None
    correct_answers_name = None
    correct_answers_count = None
    quiz_answers = None
    if lang == 'uz':
        quiz_id = f"ID{pk} тест натижалари"
        correct_answers_name = "🔑 Тўғри жавоб берилган:"
        correct_answers_count = f"{quiz.result_count} саволдан ({quiz.result_percentage})"
        theme_name = theme.name_uz
        theme = "💡 Мавзу:"
        quiz_answers = list()
        question_qs = Question.objects.filter(theme_id=theme_id)
        for q in question_qs:
            ans_ls = list()
            d = dict()
            d['id'] = q.id
            d['name'] = q.text_uz
            d['image'] = q.image_path if q.image_path else 0
            for a in q.answers.all():
                da = dict()
                da['id'] = a.id
                da['name'] = a.text_uz
                da['is_correct'] = a.is_correct
                if quiz.answers.filter(answer_id=a.id, question_id=q.id).exists():
                    da['user_selected'] = True
                else:
                    da['user_selected'] = False
                ans_ls.append(da)
            d['answers'] = ans_ls
            quiz_answers.append(d)
    elif lang == 'ru':
        quiz_id = f"ID{pk} результаты теста"
        correct_answers_name = "🔑 Правильный ответ:"
        correct_answers_count = f"{quiz.result_count} из вопроса ({quiz.result_percentage})"
        theme_name = theme.name_ru
        theme = "💡 Тема:"
        quiz_answers = list()
        question_qs = Question.objects.filter(theme_id=theme_id)
        for q in question_qs:
            ans_ls = list()
            d = dict()
            d['id'] = q.id
            d['name'] = q.text_ru
            d['image'] = q.image_path if q.image_path else 0
            for a in q.answers.all():
                da = dict()
                da['id'] = a.id
                da['name'] = a.text_ru
                da['is_correct'] = a.is_correct
                if quiz.answers.filter(answer_id=a.id, question_id=q.id).exists():
                    da['user_selected'] = True
                else:
                    da['user_selected'] = False
                ans_ls.append(da)
            d['answers'] = ans_ls
            quiz_answers.append(d)
    ctx = {
        'theme': theme,
        'theme_name': theme_name,
        'id': quiz_id,
        'quizzes': quiz_answers,
        'correct_answers_name': correct_answers_name,
        'correct_answers_count': correct_answers_count,
        'created_at': quiz.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    }
    return render(req, 'result-detail.html', context=ctx)


def about_view(request):
    obj = About.objects.first()
    lang = request.GET.get('lang')
    title = ""
    text = ""
    if lang == 'uz':
        title = "Бот ҳақида қисқача"
        text = obj.text_uz
    elif lang == 'ru':
        title = "Вкратце о боте"
        text = obj.text_ru
    return render(request, 'about.html', context={'title': title, 'text': text})


class FeedbackView(views.APIView):
    def post(self, request, *args, **kwargs):
        user = TelegramUser.objects.filter(telegram_id=self.kwargs.get('pk')).first()
        txt = f"{user.name}[{user.phone_number}]: {self.request.data.get('message')}"
        requests.get(
            url=f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage?chat_id={settings.GROUP_ID}&text={txt}")
        return response.Response(status=200)


class PaymentTypeView(generics.ListAPIView):
    queryset = PaymentType.objects.filter(is_active=True)
    serializer_class = PaymentTypeSerializer


class RateView(generics.ListAPIView):
    queryset = Rate.objects.filter(is_active=True)
    serializer_class = RateSerializer


class CheckSubscriberView(views.APIView):
    def get(self, request, *args, **kwargs):
        user = TelegramUser.objects.filter(telegram_id=self.kwargs['pk']).first()
        if user is None:
            return response.Response(status=404)
        obj = Subscription.objects.filter(user_id=user.id).first()
        if obj is None:
            return response.Response(status=400)
        if obj.end_at < date.today():
            return response.Response(status=400)
        return response.Response({'end_at': obj.end_at.strftime('%d.%m.%Y')}, status=200)


class BuySubscriberView(views.APIView):
    def post(self, request, *args, **kwargs):
        user = TelegramUser.objects.filter(telegram_id=self.kwargs['pk']).first()
        rate = Rate.objects.filter(id=self.request.data['id']).first()
        subscription = user.subscriptions.first()
        if subscription is None:
            end_at = date.today() + timedelta(days=rate.days)
            subscription = Subscription.objects.create(user_id=user.id, rate_id=rate.id, end_at=end_at)
        else:
            subscription.end_at += timedelta(days=rate.days)
            subscription.rate_id = rate.id
            subscription.save()
        Payment.objects.create(user_id=user.id, provider_id=self.request.data['provider_id'], rate_id=rate.id)
        return response.Response({'end_at': subscription.end_at.strftime('%d.%m.%Y')})


class InformationView(views.APIView):
    def get(self, request):
        obj = Information.objects.first()
        serializer = InformationSerializer(obj)
        return response.Response(serializer.data)


class TelegramUserView(views.APIView):
    def get(self, request, *args, **kwargs):
        qs = TelegramUser.objects.all()
        serializer = TelegramUserSerializer(qs, many=True)
        return response.Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user = TelegramUser.objects.filter(telegram_id=self.request.data['telegram_id']).first()
        if user is None:
            return response.Response(status=404)
        user.lang = self.request.data['lang']
        user.save()
        qs = TelegramUser.objects.all()
        serializer = TelegramUserSerializer(qs, many=True)
        return response.Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = TelegramUserSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        qs = TelegramUser.objects.all()
        serializer = TelegramUserSerializer(qs, many=True)
        return response.Response(serializer.data)


class UserView(views.APIView):
    def get(self, request, *args, **kwargs):
        user = TelegramUser.objects.filter(telegram_id=self.kwargs['pk']).first()
        if user is None:
            return response.Response(status=404)
        return response.Response(status=200)

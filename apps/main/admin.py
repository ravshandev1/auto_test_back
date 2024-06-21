from django.contrib import admin
from .models import About, Information, Subscription, TelegramUser, Rate, PaymentType, Question, Answer, \
    Theme, Quiz, QuizAnswer, Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'provider', 'rate', 'created_at']
    list_filter = ['provider']


class QuizAnswerInline(admin.StackedInline):
    model = QuizAnswer
    extra = 0
    can_delete = False


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [QuizAnswerInline]
    list_display = ['id', 'user', 'theme', 'quizzes_count', 'correct_answers_count', 'created_at']

    def quizzes_count(self, obj):
        return obj.theme.questions.count()

    def correct_answers_count(self, obj):
        qs = obj.answers.all()
        cntr = 0
        for i in qs:
            if i.answer.is_correct:
                cntr += 1
        return cntr


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ['id', 'theme', 'text_uz', 'text_ru', 'image']


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'name', 'phone_number']


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_uz', 'name_ru']


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_uz', 'name_ru', 'days', 'price']
    list_filter = ['is_active']


@admin.register(PaymentType)
class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'token']
    list_filter = ['is_active']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'rate', 'end_at']
    list_filter = ['rate']


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ['id', 'text_uz']


@admin.register(Information)
class InformationAdmin(admin.ModelAdmin):
    list_display = ['id', 'image']

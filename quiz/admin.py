from django.contrib import admin
from .models import Course, Question, Score, QuizToken


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class CourseAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ['course_name', 'questions_count']

    def questions_count(self, object):
        print(object)
        return object.question_set.all().count()


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'pub_date',
                    'course', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False


class ScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'score', 'course']


class TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'date',
                    'still_active')
    list_filter = ['date']
    search_fields = ['user_id']


admin.site.register(Course, CourseAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(QuizToken, TokenAdmin)

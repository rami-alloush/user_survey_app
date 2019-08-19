from django.contrib.admin import ModelAdmin, TabularInline, site
from .models import Course, Chapter, Question, Score, QuizToken


class ChapterInline(TabularInline):
    model = Chapter
    extra = 1


class QuestionInline(TabularInline):
    model = Question
    extra = 1


class CourseAdmin(ModelAdmin):
    inlines = [ChapterInline]
    list_display = ['course_name', 'chapters_count']

    def chapters_count(self, object):
        return object.chapter_set.all().count()


class ChapterAdmin(ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('course', 'chapter_name', 'questions_count',)

    def questions_count(self, object):
        return object.question_set.all().count()


class QuestionAdmin(ModelAdmin):
    list_display = ('question_text', 'pub_date',
                    'chapter', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False


class ScoreAdmin(ModelAdmin):
    list_display = ['user', 'score', 'course', 'date']


class TokenAdmin(ModelAdmin):
    list_display = ('user', 'token', 'date', 'course',
                    'still_active')
    list_filter = ['date']
    search_fields = ['user_id']


site.register(Course, CourseAdmin)
site.register(Chapter, ChapterAdmin)
site.register(Question, QuestionAdmin)
site.register(Score, ScoreAdmin)
site.register(QuizToken, TokenAdmin)

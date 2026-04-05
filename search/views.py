from django.shortcuts import render
from django.db.models import Q
from django.views.generic import View
# 🚨 Program을 지우고, 우리가 만든 CourseCategory와 Course를 불러옵니다.
from course.models import Course, CourseCategory

class SearchView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        context = {'query': query}

        if query:
            # 1. 강의(Course) 검색
            courses = Course.objects.filter(
                Q(title__icontains=query) | 
                Q(summary__icontains=query) | 
                Q(code__icontains=query)
            ).distinct()
            
            # 2. 트랙(CourseCategory) 검색
            categories = CourseCategory.objects.filter(
                Q(title__icontains=query) | 
                Q(summary__icontains=query)
            ).distinct()

            context['courses'] = courses
            context['categories'] = categories
            context['count'] = courses.count() + categories.count()
        
        return render(request, 'search/search_view.html', context)
import datetime

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, views
from rest_framework.response import Response

from studies.models import Study
from studies.serializer import StudySerializers

from studies.utils import RequestHandler


"""
    작성자 : 강정희
    Django REST Framework APIView, ORM을 사용한 list, retrieve view
"""
class StudyList(views.APIView, RequestHandler):
    """
        임의의 필터링을 거친 임상시험과제 리스트 조회 API
        파라미터 weekly=True 값이 반환되었을 때, 최근 일주일간 업데이트가 이루어진 데이터 조회
        파라미터 offset, limit 값으로(default = 0, 10) offset-limit pagination 구현
        (파라미터 page, page_size 값이 존재할 때, page-page_size pagination 구현)
    """
    serializer_class = StudySerializers

    def get(self, request):
        day_7days = datetime.datetime.now() - datetime.timedelta(days=7)
        day_now = datetime.datetime.now()

        # 파라미터 필터링 정보를 포함한 base query
        query = self.set_query(request)

        # 파라미터 중 weekly가 있을 때, 최근 일주일간 업데이트 데이터 조회
        if self.has_weekly(request):
            query &= Q(updated_at__range=[f'{day_7days}', f'{day_now}'])

        # 파라미터 중 page, page_size가 있을 때, pagination 추가(default 값은 offset, limit)
        if request.GET.get('page') or request.GET.get('page_size'):
            offset, limit = self.page_page_size_paginatior(request)
        else:
            offset, limit = self.offset_limit_paginator(request)

        studies = Study.objects.filter(query)[offset:offset+limit]
        serializer = self.serializer_class(studies, many=True)

        return Response(serializer.data)


class StudyRetrieve(views.APIView):
    """
        지정된 uuid(number)의 임상시험과제 상세 조회 API
    """
    serializer_class = StudySerializers

    def get_object(self, pk):
        return get_object_or_404(Study, pk=pk)

    def get(self, request, pk):
        # pk 값과 맞는 object 검색 후 없다면 404 error 반환
        study = self.get_object(pk)
        serializer = self.serializer_class(study)

        return Response(serializer.data)


"""
    작성자 : 김채욱
    Django REST Framework GenericView, 내장 클래스을 사용한 list, retrieve view   
"""
# class StudyList(generics.ListAPIView):
#     """
#         최근 일주일간 업데이트가 이루어지고, 임의의 필터링을 거친 임상시험과제 리스트 조회 API
#         settings.py-'DEFAULT_PAGINATION_CLASS','PAGE_SIZE' 선언으로 page,page_size pagination 구현
#     """
#     day_7days = datetime.datetime.now()-datetime.timedelta(days=7)
#     day_now = datetime.datetime.now()
#
#     # 최근 일주일간 업데이트 데이터로 조회
#     queryset = Study.objects.all().filter(updated_at__range=[f'{day_7days}', f'{day_now}'])
#     serializer_class = StudySerializers
#
#     # rest-framework filter 내장 클래스를 이용한 필터링
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['number', 'title', 'institute__name']
#
#
# class StudyRetrieve(generics.RetrieveAPIView):
#     """
#         지정된 uuid(number)의 임상시험과제 상세 조회 API
#     """
#     queryset = Study.objects.all()
#     serializer_class = StudySerializers

from __future__ import unicode_literals
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import FaqForm

@login_required

#########################################################################
# main page
#########################################################################
# Create your views here.
def main(request):
    return render(request, 'test_main.html')


#########################################################################
# custom function
#########################################################################
# 테스팅 용도
def get_key():
    with open('static/other/keyfile.lst', encoding='utf-8') as txtfile:
        for row in txtfile.readlines():
            key = row

    return key

#########################################################################
# testing page
#########################################################################

def page(request):
    if request.method == 'POST':
        faq_id= request.POST['faq_id']
        faq_type= request.POST['faq_type']
        faq_question= request.POST['faq_question']
        faq_answer= request.POST['faq_answer']

        faq_list = Faq.objects.filter(
            faq_id__startswith=faq_id,
            faq_type__startswith=faq_type,
            faq_question__startswith=faq_question,
            faq_answer__startswith=faq_answer
        ).order_by('-id')

        paginator = Paginator(faq_list, 15)
        page = request.GET.get('page')
        faqs = paginator.get_page(page)
        context = {'faqs': faqs}
        return render(request, 'test_page.html', context)

    else:
        faq_list = Faq.objects.all().order_by('-id')
        paginator = Paginator(faq_list, 15)
        page = request.GET.get('page')
        faqs = paginator.get_page(page)
        context = {'faqs': faqs}
        return render(request, 'test_page.html', context)


def page_insert(request):
    if request.method == 'POST':
        form = FaqForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/testing/page')
    else:
        form = FaqForm()

    return render(request, 'test_page.html', {'form': form})


def page_delete(request):
    if request.method == 'POST':
        getObject= Faq.objects.get(id = request.POST['id'])
        getObject.delete()
        return redirect('/testing/page')

    return render(request, 'test_page.html')

def page_update(request):
    if request.method == 'POST':
        getObject = Faq.objects.get(id = request.POST['id']) # pk에 해당하는 업데이트 대상을 가져옴
        form = FaqForm(request.POST) # 입력값 가져옴

        if form.is_valid():
            #print(form.cleaned_data) # 콘솔 찍기. 디버깅

            getObject.faq_id = form.cleaned_data['faq_id']
            getObject.faq_type = form.cleaned_data['faq_type']
            getObject.faq_question = form.cleaned_data['faq_question']
            getObject.faq_answer = form.cleaned_data['faq_answer']
            getObject.save()

        return redirect('/testing/page')

    else:
        form = FaqForm()

    return render(request, 'test_page.html', {'form': form})


#########################################################################
# testing graph
#########################################################################

def graph(request):
    return render(request, 'test_graph.html')


#########################################################################
# testing post
# AJAX UnLimit Scrolling Test
#########################################################################

def post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        read = request.POST.get('read')

        read_list = Post.objects.all().order_by('read').values('read').distinct()
        context = {'read_list': read_list, 'title': title, 'content': content, 'read': read}
        return render(request, 'test_post.html', context)

    else:
        read_list = Post.objects.all().order_by('read').values('read').distinct()
        context = {'read_list': read_list}
        return render(request, 'test_post.html', context)

    #try:
    #    post_list = paginator.page(page)
    #except PageNotAnInteger:
    #    post_list = paginator.page(1)
    #except EmptyPage:
    #    post_list = paginator.page(paginator.num_pages)

    #title = request.POST['title']
    #content = request.POST['content']
    #callmorepostFlag = 'true'

    #context = {'post_list': post_list}
    #context = {'post_list': post_list, 'callmorepostFlag': callmorepostFlag,
    #           'title': title, 'content': content}
    #return render(request, 'test_post_ajax.html', context)


def post_ajax(request): #Ajax 로 호출하는 함수

    if request.method == 'POST':

        title = request.POST.get('title')
        content = request.POST.get('content')
        read = request.POST.get('read')
        callmorepostFlag = 'true'

        print("--------------------------------------------------------------------------------------------------- read : " + read)

        post_list = Post.objects.filter(
            title__contains=title,
			content__contains=content,
            read__contains=read
		).order_by('-id')

        page = int(request.POST.get('page'))

        #print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        #print("ajax 타이틀 : " + str(title))
        #print("ajax 컨텐츠 : " + str(content))
        #print("page : " + str(page))
        total_count = post_list.count()
        page_max = round(post_list.count() / 15)

        #print("count : " + str(total_count))
        #print("page max : " + str(page_max))
        #print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

        paginator = Paginator(post_list, page * 15)

        try:
            if int(page) >= page_max : # 마지막 페이지 멈춤 구현
                post_list = paginator.get_page(1)
                callmorepostFlag = 'false'

            else:
                post_list = paginator.get_page(1)

        except PageNotAnInteger:
            post_list = paginator.get_page(1)
        except EmptyPage:
            post_list = paginator.get_page(paginator.num_pages)

        context = {'post_list': post_list,
                   'total_count': total_count, 'callmorepostFlag': callmorepostFlag,
                   'title': title, 'content': content, 'read': read}
        return render(request, 'test_post_ajax.html', context)

    else:
        return render(request, 'test_post.html')





#########################################################################
# server_list test
#########################################################################

def test1(request):
    return render(request, 'test1.html')

def test2(request):
    return render(request, 'test2.html')

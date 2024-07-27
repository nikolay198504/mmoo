from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Bill, Comment, Category
from .forms import CommentForm, BillForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import User
from .tasks import comment_send_email, comment_accept_send_email
from .filters import BillFilter


class BillList(ListView):
    model = Bill
    template_name = 'bill_list.html'
    context_object_name = 'bills'
    ordering = '-bill_time'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BillDetail(LoginRequiredMixin, DetailView):
    model = Bill
    template_name = 'bill_detail.html'
    context_object_name = 'bill'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bill_author = Bill.objects.get(id=self.kwargs['pk']).author
        context['is_author'] = self.request.user == bill_author
        comments_authors = Comment.objects.filter(comment_bill=self.kwargs['pk']).values('author')
        context['comment'] = {'author': self.request.user.id} in comments_authors
        return context


class BillCreate(LoginRequiredMixin, CreateView):
    form_class = BillForm
    model = Bill
    template_name = 'bill_edit.html'
    context_object_name = 'bill_create'
    success_url = reverse_lazy('bill_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = User.objects.get(id=self.request.user.id)
        post.save()
        return redirect(f'/bill/{post.id}')


class BillUpdate(LoginRequiredMixin, UpdateView):
    form_class = BillForm
    model = Bill
    template_name = 'bill_edit.html'
    success_url = '/create/'


    def dispatch(self, request, *args, **kwargs):
        author = Bill.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Редактировать объявление может только его автор")

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Bill.objects.get(pk=id)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect('/bill/' + str(self.kwargs.get('pk')))


class BillDelete(LoginRequiredMixin, DeleteView):
    model = Bill
    template_name = 'bill_delete.html'
    success_url = reverse_lazy('bill_list')

    def dispatch(self, request, *args, **kwargs):
        author = Bill.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Удалить объявление может только его автор")


class CommentList(ListView):
    model = Comment
    template_name = 'mycomments.html'
    ordering = '-date_in'
    context_object_name = 'mycomments'

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = Comment.objects.filter(comment_bill__author=user_id).order_by('-date_in')
        self.filterset = BillFilter(self.request.GET, queryset, request=self.request.user.id)
        return self.filterset.qs


    # def get_queryset(self):
    #     queryset = Comment.objects.filter(comment_bill__author=self.request.user).order_by('-date_in')
    #     self.filterset = BillFilter(self.request.GET, queryset, request=self.request.user)
    #     return self.filterset.qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


# class CommentCreate(LoginRequiredMixin, CreateView):
#     form_class = CommentForm
#     model = Comment
#     template_name = 'respond.html'
#
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['bill_detail'] = Bill.objects.get(pk=self.kwargs['pk']).title
#         return context
#
#     def form_valid(self, form):
#         comment = form.save(commit=False)
#         comment.author = self.request.user
#         comment.comment_bill = Bill.objects.get(id=self.kwargs['pk'])
#         return super().form_valid(form)
#

class CommentDelete(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'comment_delete.html'
    success_url = reverse_lazy('mycomments')

    def get_object(self, **kwargs):
        my_id = self.kwargs.get('pk')
        return Comment.objects.get(pk=my_id)


class CategoryList(BillList):
    model = Bill
    template_name = 'category_list.html'
    context_object_name = 'bill_cat_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Bill.objects.filter(category=self.category).order_by('-bill_time')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class Respond(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'respond.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        respond = form.save(commit=False)
        respond.author = User.objects.get(id=self.request.user.id)
        respond.comment_bill = Bill.objects.get(id=self.kwargs.get('pk'))
        respond.save()
        comment_send_email.delay(respond.id)
        return redirect(f'/bill/{self.kwargs.get("pk")}/')


class ConfirmUser(UpdateView):
    model = User
    context_object_name = 'confirm_user'

    def post(self, request, *args, **kwargs):
        if 'code' in request.POST:
            user = User.objects.filter(code=request.POST['code'])
            if user.exists():
                user.update(is_active=True)
                user.update(code=None)
            else:
                return render(self.request, 'invalid_code.html')
        return redirect('account_login')


# @login_required
# def accept_comment(request, pk):
#     comment = Comment.objects.get(id=pk)
#     comment.accepted = True
#     comment.save()
#     return HttpResponseRedirect(reverse('mycomments'))

@login_required
def accept_comment(request, **kwargs):
    if request.user.is_authenticated:
        comment = Comment.objects.get(id=kwargs.get('pk'))
        comment.status = True
        comment.save()
        comment_accept_send_email.delay(comment_bill_id=comment.id)
        return HttpResponseRedirect('/mycomments')
    else:
        return HttpResponseRedirect('/accounts/login')

@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    return redirect('bill_cat_list', pk)
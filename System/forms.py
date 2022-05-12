from django import forms
class SearchForm(forms.Form):
    CHOICES = [
        (u'GA', u'GA'),
        (u'传统调度方法', u'传统调度方法'),
    ]

    search_by = forms.ChoiceField(
        label='',
        choices=CHOICES,
        widget=forms.RadioSelect(),
        initial=u'书名',
    )

    keyword = forms.CharField(
        label='',
        max_length=32,
        widget=forms.TextInput(attrs={
            'class': 'form-control input-lg',
            'placeholder': u'请上传所需要调度的任务数据',
            'name': 'keyword',
        })
    )
from django import forms


class LogForm(forms.Form):

    log_line = forms.CharField(
        label="Enter Log Line",
        required=True,
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'cols': 60,
                'placeholder': 'Example: admin | 192.168.1.1 | /login | 500 | 1200ms',
                'class': 'form-control'
            }
        )
    )
from django import forms


class PlaylistForm(forms.Form):
    playlist_url = forms.URLField(label='YouTube Playlist URL')

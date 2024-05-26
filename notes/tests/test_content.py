from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesPage(TestCase):

    NOTES_LIST = reverse('notes:list')
    NOTES_COUNT_ON_NOTES_LIST = 10

    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='Лев Толстой')
        cls.other_user = User.objects.create(username='Саня Пушкин')

        cls.notes = [
            Note(
                author=cls.author,
                title=f'Запись {index}',
                text='Текст',
                slug=f'zapis-{index}'
            )
            for index in range(cls.NOTES_COUNT_ON_NOTES_LIST)
        ]
        Note.objects.bulk_create(cls.notes)

        cls.notes = list(Note.objects.filter(author=cls.author))
        cls.other_note = Note.objects.create(
            author=cls.other_user,
            title='Чужая заметка',
            text='Текст чужой заметки',
            slug='chuzhaya-zametka'
        )

    def test_note_in_object_list(self):

        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST)
        object_list = response.context['object_list']

        self.assertIn(self.notes[0], object_list)

    def test_other_user_notes_not_in_list(self):

        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST)
        object_list = response.context['object_list']

        self.assertNotIn(self.other_note, object_list)

    def test_note_add_page_contains_form(self):

        self.client.force_login(self.author)
        add_url = reverse('notes:add')
        response = self.client.get(add_url)

        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_edit_page_contains_form(self):

        self.client.force_login(self.author)
        edit_url = reverse('notes:edit', args=(self.notes[0].slug,))
        response = self.client.get(edit_url)

        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_notes_count(self):

        self.client.force_login(self.author)

        response = self.client.get(self.NOTES_LIST)
        notes_count = response.context['object_list'].count()

        self.assertEqual(notes_count, self.NOTES_COUNT_ON_NOTES_LIST)

    def test_notes_order(self):

        self.client.force_login(self.author)

        response = self.client.get(self.NOTES_LIST)
        object_list = response.context['object_list']

        all_notes = [note.id for note in object_list]
        sorted_dates = sorted(all_notes)

        self.assertEqual(all_notes, sorted_dates)

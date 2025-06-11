import factory
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import AISupportSession, AISupportMessage

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'testuser{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class AISupportSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AISupportSession

    user = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f'テストセッション {n}')
    description = factory.Faker('text', locale='ja_JP')
    status = 'active'
    started_at = factory.LazyFunction(timezone.now)
    last_interaction_at = factory.LazyFunction(timezone.now)

class AISupportMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AISupportMessage

    session = factory.SubFactory(AISupportSessionFactory)
    message_type = 'user'
    content = factory.Faker('text', locale='ja_JP')
    created_at = factory.LazyFunction(timezone.now) 
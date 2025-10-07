import pytest
from django.utils import timezone
from django_basemodels.test_app.models import TestBaseModel

# импортируем сериализатор вашего пакета.
# Если путь к сериализатору другой, замените строку ниже.
from django_basemodels_rest.serializers import BaseModelSerializer


@pytest.mark.django_db
def test_meta_init_subclass_sets_read_only_fields():
    """
    Проверяем, что Meta.__init_subclass__ в сериализаторе корректно вычисляет read_only_fields.
    """
    class MySerializer(BaseModelSerializer):
        class Meta(BaseModelSerializer.Meta):
            model = TestBaseModel
            fields = BaseModelSerializer.Meta.fields + ("title", "is_active", "polymorphic_ctype")
            writable_fields = ("title",)

    expected = tuple(
        f
        for f in MySerializer.Meta.fields
        if f not in tuple(getattr(MySerializer.Meta, "writable_fields", ())) + ("pk", "created_at", "updated_at")
    )

    assert tuple(MySerializer.Meta.read_only_fields) == expected


@pytest.mark.django_db
def test_serializer_fields_and_representation():
    """
    Проверяем поля сериализатора, их read_only-флаги и содержание to_representation.
    """
    class MySerializer(BaseModelSerializer):
        class Meta(BaseModelSerializer.Meta):
            model = TestBaseModel
            fields = BaseModelSerializer.Meta.fields + ("title", "is_active", "polymorphic_ctype")
            writable_fields = ("title",)

    now = timezone.now()
    obj = TestBaseModel.objects.create(title="test-title", is_active=True, active_start=now - timezone.timedelta(days=1))

    serializer = MySerializer(instance=obj)

    # Проверяем наличие полей
    for f in ("pk", "created_at", "updated_at", "active_start", "active_end", "title", "is_active", "polymorphic_ctype"):
        assert f in serializer.fields

    # writable_fields: title -> writable, others -> read_only (соответственно Meta)
    assert serializer.fields["title"].read_only is False
    assert serializer.fields["active_start"].read_only is True

    # Представление содержит is_active и polymorphic_ctype
    data = serializer.data
    assert "is_active" in data
    assert data["is_active"] == obj.is_active_real
    assert "polymorphic_ctype" in data
    assert data["polymorphic_ctype"] == obj.polymorphic_ctype.id


@pytest.mark.django_db
def test_get_methods_with_model_and_dict():
    """
    Проверяем get_is_active/get_polymorphic_ctype для model instance и dict.
    """
    class MySerializer(BaseModelSerializer):
        class Meta(BaseModelSerializer.Meta):
            model = TestBaseModel
            fields = BaseModelSerializer.Meta.fields + ("title", "is_active", "polymorphic_ctype")
            writable_fields = ("title",)

    obj = TestBaseModel.objects.create(title="x", is_active=False)

    serializer = MySerializer()

    # Для модели
    assert serializer.get_is_active(obj) == obj.is_active_real
    assert serializer.get_polymorphic_ctype(obj) == obj.polymorphic_ctype.id

    # Для dict
    d = {"polymorphic_ctype": 123, "is_active": True}
    assert serializer.get_polymorphic_ctype(d) == 123
    assert serializer.get_is_active(d) is None
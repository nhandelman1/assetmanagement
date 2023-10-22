from abc import ABC, abstractmethod

from django.db.models import Model

from util.testcasebase import TestCaseBase


class DjangoModelTestCaseBase(TestCaseBase, ABC):

    @abstractmethod
    def equal(self, model1: Model, model2: Model):
        """ Test equality of two Django Models

        Definition of equality is determined by each subclass.

        Args:
            model1 (Model):
            model2 (Model):

        Returns:
            True if model1 equals model2. False model1 does not equal model2
        """
        raise NotImplementedError("equal() not implemented by subclass")

    def simple_equal(self, model1, model2, cls, rem_attr_list=()):
        """ Simple method for testing Model equality that is common to many Models

        In this function, model1 and model2 are considered equal if model1 and model2 are both of type cls and model1
        instance attributes and values equal those of model2 (after rem_attr_list is applied and 'id' field is removed).
        Any caller of this function should ensure that __eq__ is defined as expected for each concrete (non 'id')
        instance attribute value in _meta.get_fields().

        Args:
            model1 (Model):
            model2 (Model):
            cls (type[Model]): model1 and model2 must both be of this type
            rem_attr_list (list): remove instance attributes in this list from both model1 and model2 for comparison
                purposes. model1 and model2 are not altered. Default ()

        Raises:
            AssertionError
        """
        rem_attr_list = list(rem_attr_list) + ["id"]

        self.assertEqual(type(model1), cls)
        self.assertEqual(type(model2), cls)

        def build_dict(_model):
            return {f.name: getattr(_model, f.name) for f in _model._meta.get_fields()
                    if f.name not in rem_attr_list and f.concrete}

        self.assertEqual(build_dict(model1), build_dict(model2), cls.__name__)

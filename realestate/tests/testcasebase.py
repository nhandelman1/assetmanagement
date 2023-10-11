from abc import ABC, abstractmethod

from django.test import TestCase


class TestCaseBase(TestCase, ABC):

    @abstractmethod
    def equal(self, obj1: object, obj2: object):
        """ Test equality of two objects

        Definition of equality is determined by each subclass.

        Args:
            obj1 (object):
            obj2 (object):

        Returns:
            True if obj1 equals obj2. False obj1 does not equal obj2
        """
        raise NotImplementedError("equal() not implemented by subclass")

    def simple_equal(self, obj1, obj2, cls, rem_attr_list=()):
        """ Simple method for testing object equality that is common to many objects

        In this function, obj1 and obj2 are considered equal if obj1 and obj2 are both of type cls and
        obj1.__dict__ == obj2.__dict__ (after rem_attr_list is applied). Any caller of this function should ensure that
        __eq__ is defined as expected for each key and value in __dict__.

        Args:
            obj1 (object):
            obj2 (object):
            cls (type[object]): obj1 and obj must both be of this type
            rem_attr_list (list): remove attributes in this list from both obj1 and obj2 for comparison purposes. obj1
                obj2 are not altered. Default ()

        Raises:
            AssertionError
        """
        self.assertEqual(type(obj1), cls)
        self.assertEqual(type(obj2), cls)

        self.assertEqual({k: v for k, v in obj1.__dict__.items() if k not in rem_attr_list},
                         {k: v for k, v in obj2.__dict__.items() if k not in rem_attr_list}, cls.__name__)

# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""decorator_utils tests."""

# pylint: disable=unused-import
import functools
import time

from tensorflow.python.platform import test
from tensorflow.python.platform import tf_logging as logging
from tensorflow.python.util import decorator_utils


def _test_function(unused_arg=0):
  pass


class GetQualifiedNameTest(test.TestCase):

  def test_method(self):
    self.assertEqual(
        "GetQualifiedNameTest.test_method",
        decorator_utils.get_qualified_name(GetQualifiedNameTest.test_method))

  def test_function(self):
    self.assertEqual("_test_function",
                     decorator_utils.get_qualified_name(_test_function))


class AddNoticeToDocstringTest(test.TestCase):

  def _check(self, doc, expected):
    self.assertEqual(
        decorator_utils.add_notice_to_docstring(
            doc=doc,
            instructions="Instructions",
            no_doc_str="Nothing here",
            suffix_str="(suffix)",
            notice=["Go away"]),
        expected)

  def test_regular(self):
    expected = (
        "Brief (suffix)\n\nWarning: Go away\nInstructions\n\nDocstring\n\n"
        "Args:\n  arg1: desc")
    # No indent for main docstring
    self._check("Brief\n\nDocstring\n\nArgs:\n  arg1: desc", expected)
    # 2 space indent for main docstring, blank lines not indented
    self._check("Brief\n\n  Docstring\n\n  Args:\n    arg1: desc", expected)
    # 2 space indent for main docstring, blank lines indented as well.
    self._check("Brief\n  \n  Docstring\n  \n  Args:\n    arg1: desc", expected)
    # No indent for main docstring, first line blank.
    self._check("\n  Brief\n  \n  Docstring\n  \n  Args:\n    arg1: desc",
                expected)
    # 2 space indent, first line blank.
    self._check("\n  Brief\n  \n  Docstring\n  \n  Args:\n    arg1: desc",
                expected)

  def test_brief_only(self):
    expected = "Brief (suffix)\n\nWarning: Go away\nInstructions"
    self._check("Brief", expected)
    self._check("Brief\n", expected)
    self._check("Brief\n  ", expected)
    self._check("\nBrief\n  ", expected)
    self._check("\n  Brief\n  ", expected)

  def test_no_docstring(self):
    expected = "Nothing here\n\nWarning: Go away\nInstructions"
    self._check(None, expected)
    self._check("", expected)

  def test_no_empty_line(self):
    expected = "Brief (suffix)\n\nWarning: Go away\nInstructions\n\nDocstring"
    # No second line indent
    self._check("Brief\nDocstring", expected)
    # 2 space second line indent
    self._check("Brief\n  Docstring", expected)
    # No second line indent, first line blank
    self._check("\nBrief\nDocstring", expected)
    # 2 space second line indent, first line blank
    self._check("\n  Brief\n  Docstring", expected)


class ValidateCallableTest(test.TestCase):

  def test_function(self):
    decorator_utils.validate_callable(_test_function, "test")

  def test_method(self):
    decorator_utils.validate_callable(self.test_method, "test")

  def test_callable(self):

    class TestClass(object):

      def __call__(self):
        pass

    decorator_utils.validate_callable(TestClass(), "test")

  def test_partial(self):
    partial = functools.partial(_test_function, unused_arg=7)
    decorator_utils.validate_callable(partial, "test")

  def test_fail_non_callable(self):
    x = 0
    self.assertRaises(ValueError, decorator_utils.validate_callable, x, "test")


class CachedClassPropertyTest(test.TestCase):

  def testCachedClassProperty(self):
    log = []  # log all calls to `MyClass.value`.

    class MyClass(object):

      @decorator_utils.cached_classproperty
      def value(cls):  # pylint: disable=no-self-argument
        log.append(cls)
        return cls.__name__

    class MySubclass(MyClass):
      pass

    # Property is computed first time it is accessed.
    self.assertLen(log, 0)
    self.assertEqual(MyClass.value, "MyClass")
    self.assertEqual(log, [MyClass])

    # Cached values are used on subsequent accesses.
    self.assertEqual(MyClass.value, "MyClass")
    self.assertEqual(MyClass.value, "MyClass")
    self.assertEqual(log, [MyClass])

    # The wrapped method is called for each subclass.
    self.assertEqual(MySubclass.value, "MySubclass")
    self.assertEqual(log, [MyClass, MySubclass])
    self.assertEqual(MySubclass.value, "MySubclass")
    self.assertEqual(MySubclass.value, "MySubclass")
    self.assertEqual(log, [MyClass, MySubclass])

    # The property can also be accessed via an instance.
    self.assertEqual(MyClass().value, "MyClass")
    self.assertEqual(MySubclass().value, "MySubclass")
    self.assertEqual(log, [MyClass, MySubclass])

    # Attempts to modify the property via an instance will fail.
    with self.assertRaises(AttributeError):
      MyClass().value = 12
    with self.assertRaises(AttributeError):
      del MyClass().value

  def testCachedClassPropertyWithTimeout(self):
    # pylint: disable=no-value-for-parameter
    log = []  # log all calls to `MyClass.value`.

    class MyClass(object):

      @decorator_utils.cached_classproperty(timeout=0.1)  # 0.1 second timeout
      def value(cls):  # pylint: disable=no-self-argument
        log.append(cls)
        return cls.__name__

    class MySubclass(MyClass):
      pass

    # Property is computed first time it is accessed.
    self.assertLen(log, 0)
    self.assertEqual(MyClass.value, "MyClass")
    self.assertEqual(log, [MyClass])

    # Cached value is used within timeout.
    self.assertEqual(MyClass.value, "MyClass")
    self.assertEqual(log, [MyClass])

    # Wait for timeout to expire.
    time.sleep(0.2)

    # Property is recomputed after timeout.
    self.assertEqual(MyClass.value, "MyClass")
    self.assertEqual(log, [MyClass, MyClass])

    # Subclass behaves independently.
    self.assertEqual(MySubclass.value, "MySubclass")
    self.assertEqual(log, [MyClass, MyClass, MySubclass])
    self.assertEqual(MySubclass.value, "MySubclass")
    self.assertEqual(log, [MyClass, MyClass, MySubclass])

  def testCachedClassPropertyResetCache(self):
    log = []  # log all calls to `MyClass.value`.

    class MyClass(object):

      @decorator_utils.cached_classproperty
      def value(cls):  # pylint: disable=no-self-argument
        log.append(cls)
        return cls.__name__

    class MySubclass(MyClass):
      pass

    # Property is computed first time it is accessed.
    self.assertLen(log, 0)
    self.assertEqual(MyClass.value, "MyClass")
    self.assertEqual(log, [MyClass])

    # Cached value is used.
    self.assertEqual(MyClass.value, "MyClass")
    self.assertEqual(log, [MyClass])

    # Reset cache and verify property is recomputed.
    MyClass.value.reset_cache(MyClass)
    self.assertEqual(MyClass.value, "MyClass")
    self.assertEqual(log, [MyClass, MyClass])

    # Subclass cache is unaffected.
    self.assertEqual(MySubclass.value, "MySubclass")
    self.assertEqual(log, [MyClass, MyClass, MySubclass])
    self.assertEqual(MySubclass.value, "MySubclass")
    self.assertEqual(log, [MyClass, MyClass, MySubclass])

    # Reset subclass cache.
    MySubclass.value.reset_cache(MySubclass)
    self.assertEqual(MySubclass.value, "MySubclass")
    self.assertEqual(log, [MyClass, MyClass, MySubclass, MySubclass])


if __name__ == "__main__":
  test.main()
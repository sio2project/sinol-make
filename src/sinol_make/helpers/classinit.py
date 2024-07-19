# From oioioi/base/utils/__init__.py

class ClassInitMeta(type):
    """Meta class triggering __classinit__ on class intialization."""

    def __init__(cls, class_name, bases, new_attrs):
        super(ClassInitMeta, cls).__init__(class_name, bases, new_attrs)
        cls.__classinit__()


class ClassInitBase(object, metaclass=ClassInitMeta):
    """Abstract base class injecting ClassInitMeta meta class."""

    @classmethod
    def __classinit__(cls):
        """
        Empty __classinit__ implementation.

        This must be a no-op as subclasses can't reliably call base class's
        __classinit__ from their __classinit__s.

        Subclasses of __classinit__ should look like:

        .. python::

            class MyClass(ClassInitBase):

                @classmethod
                def __classinit__(cls):
                    # Need globals().get as MyClass may be still undefined.
                    super(globals().get('MyClass', cls),
                            cls).__classinit__()
                    ...

            class Derived(MyClass):

                @classmethod
                def __classinit__(cls):
                    super(globals().get('Derived', cls),
                            cls).__classinit__()
                    ...
        """
        pass


class RegisteredSubclassesBase(ClassInitBase):
    """A base class for classes which should have a list of subclasses
    available.

    The list of subclasses is available in their :attr:`subclasses` class
    attributes. Classes which have *explicitly* set :attr:`abstract` class
    attribute to ``True`` are not added to :attr:`subclasses`.
    """

    _subclasses_loaded = False

    @classmethod
    def __classinit__(cls):
        this_cls = globals().get('RegisteredSubclassesBase', cls)
        super(this_cls, cls).__classinit__()
        if this_cls is cls:
            # This is RegisteredSubclassesBase class.
            return

        assert 'subclasses' not in cls.__dict__, (
            '%s defines attribute subclasses, but has '
            'RegisteredSubclassesMeta metaclass' % (cls,)
        )
        cls.subclasses = []
        cls.abstract = cls.__dict__.get('abstract', False)

        def find_superclass(cls):
            superclasses = [c for c in cls.__bases__ if issubclass(c, this_cls)]
            if not superclasses:
                return None
            if len(superclasses) > 1:
                raise AssertionError(
                    '%s derives from more than one '
                    'RegisteredSubclassesBase' % (cls.__name__,)
                )
            superclass = superclasses[0]
            return superclass

        # Add the class to all superclasses' 'subclasses' attribute, including
        # self.
        superclass = cls
        while superclass is not this_cls:
            if not cls.abstract:
                superclass.subclasses.append(cls)
            superclass = find_superclass(superclass)

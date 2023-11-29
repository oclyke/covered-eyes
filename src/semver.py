# https://semver.org/


# compare metadata sets according to semver
# returns 1 if set_a has precedence over set_b
# returns 0 if the sets are equal
# returns -1 if set_b has precedence over set_a
def compare_meta(set_a, set_b):
    # if both sets are empty at the same time they are equal
    if (not len(set_a)) and (not len(set_b)):
        return 0

    # we know at least one set has items remaining
    # if one set empties first it has lower precedence
    if (not len(set_a)) or (not len(set_b)):
        return 1 if not len(set_b) else -1

    # both sets have items to compare at this level
    a = set_a.pop(0)
    b = set_b.pop(0)

    try:
        if int(a) == int(b):
            return compare_meta(set_a, set_b)
        return 1 if int(a) > int(b) else -1
    except ValueError:
        if str(a) == str(b):
            return compare_meta(set_a, set_b)
        return 1 if str(a) > str(b) else -1


# esure returned object is of type
def ensure_type(T):
    def decorator(f):
        def inner(*args, **kwargs):
            return T(f(*args, **kwargs))

        return inner

    return decorator


# class to operate on version numbers
class SemanticVersion:
    # determine if input string takes precedence over this version using semantic versioning
    # returns 0 if versions are the same
    # returns 1 if a has higher precedence
    # returns -1 if a has lower precedence
    @staticmethod
    def precedence(a, b):
        a = SemanticVersion.conform(a)
        b = SemanticVersion.conform(b)

        # first compare the major.minor.patch portion
        if a.major != b.major:
            return 1 if a.major > b.major else -1
        if a.minor != b.minor:
            return 1 if a.minor > b.minor else -1
        if a.patch != b.patch:
            return 1 if a.patch > b.patch else -1

        # if they are both release versions then they match
        if (not a.is_prerelease) and (not b.is_prerelease):
            return 0

        # now we know at least one is not a release version
        # if one is a release version then it will take precedeece
        if (not a.is_prerelease) or (not b.is_prerelease):
            return 1 if (not a.is_prerelease) else -1

        # now both are known to be prerelease versions
        if a.metadata != b.metadata:
            a = a.metadata.split(".")
            b = b.metadata.split(".")
            return compare_meta(a, b)

        # since the metadata strings matched these two versions have equal precedence
        return 0

    @staticmethod
    def conform(input):
        try:
            input._is_semver
            return input
        except AttributeError:
            if isinstance(input, str):
                return SemanticVersion.from_semver(input)
            raise TypeError("cannot conform input to semver")

    @classmethod
    def from_semver(cls, input):
        try:
            (numeral, metadata) = input.split("-", 1)
        except ValueError:
            numeral = input
            metadata = None
        (major, minor, patch) = numeral.split(".", 2)
        return cls(major, minor, patch, metadata)

    @staticmethod
    def match(a, b):
        return (
            True
            if SemanticVersion.conform(a).matches(SemanticVersion.conform(b))
            else False
        )

    def __init__(self, major, minor, patch, metadata=None):
        self._is_semver = True
        self._major = major
        self._minor = minor
        self._patch = patch
        self._metadata = metadata

    @property
    @ensure_type(int)
    def major(self):
        return self._major

    @property
    @ensure_type(int)
    def minor(self):
        return self._minor

    @property
    @ensure_type(int)
    def patch(self):
        return self._patch

    @property
    def is_prerelease(self):
        return (self._metadata is not None) and (self._metadata is not "")

    @property
    @ensure_type(str)
    def metadata(self):
        return self._metadata

    def to_string(self):
        # return f'{self.major}.{self.minor}.{self.patch}{"" if not self.is_prerelease "-"}{"" if not self.is_prerelease else self.metadata}'
        res = str(self.major) + "." + str(self.minor) + "." + str(self.patch)
        if self.is_prerelease:
            res += "-" + self.metadata
        return res

    # check if this version comes before the version b
    # returns True if the version b is preceded by this version
    # a result of True means that version b is an upgrade
    def precedes(self, b):
        return (
            True
            if (SemanticVersion.precedence(SemanticVersion.conform(b), self) == 1)
            else False
        )

    # checks if this version comes after version b
    # returns True if version b precedes this version
    # a result of True means that this version is an upgrade over version b
    def succeeds(self, b):
        return (
            True
            if (SemanticVersion.precedence(SemanticVersion.conform(b), self) == -1)
            else False
        )

    # checks if versions are equivalent
    def matches(self, b):
        return (
            True
            if (SemanticVersion.precedence(SemanticVersion.conform(b), self) == 0)
            else False
        )

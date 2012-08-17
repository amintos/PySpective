#
#   PYTHON BDD/SPEC TEST RUNNER
#   ...a simple way of writing specs
#   (but an unflexible way of implementing a spec runner - so please help!)
#
#   (c) 2012 | Toni Mattis | https://github.com/amintos
#
#   Placed under the MIT License:
#   http://opensource.org/licenses/mit-license.php/
#

"""
Simple BDD spec runner. Structure of a spec test:

    with describe("The DeepThought component") as it:

        with it("answers correctly") as then:
            x = DeepThought()
            then(x.answer()).should.be(42)

        with it("...") as then:
            ...

    with describe("...") as it:
        ...

Supported assertions after .should / .should_not:

    Assertion method                    Subject requirements
    --------------------------------------------------------
    be(a_value)
    < a_value
    > a_value
    <= a_alue
    >= a_value
    have(an_attribute_name)
    contain(an_element)                 Iterable
    match(a_regular_expression)         String
    throw(an_exception_class)           Callable
    
    

How this works:
    describe("a feature") returns a callable Feature object,
    please name it 'it'.

    The call to the Feature object it("behaves") returns a callable
    Case object, please name it 'then'.

    Each call to the Case object returns a Target object wrapping the
    given subject. 
    The Target properties 'should' and 'should_not' return either the
    Subject itself or a negated version. The following assertion refers
    to the wrapped subject and may take another argument.

    done() prints the final results and exits. The exit code indicates
    the number of failed tests. Use done(exit=False) to continue code
    execution.

    All events are recorded using a global TestResult object residing
    in 'main_result'.
"""

# TODO: Support contexts, example:
# with it.in_context("being in a context"):
#   with it("behaves this way") as then:
#       ...
# with it.in_context("being in another context"):
#   with it("behaves the other way") as then:
#       ...

# TODO: Support fixtures
# with describe("a feature") as it:
#
#   @before(it)
#   def setup(it):
#       it.mock = MyMock()
#
#   @after(it)
#   def teardown(it):
#       del it.mock


import sys
import re

# ------------------------------------------------------------------------------
class Void(object):
    """A placeholder for nothing (with proper __repr__)"""
    def __repr__(self):
        return ''
    __str__ = __repr__
Void = Void()

# ------------------------------------------------------------------------------
class TestResult(object):
    """The standard test result formatter"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def enter_feature(self, feature):
        """A new feature is being tested now"""
        print feature.what

    def enter_case(self, case):
        """A test case of a feature is being executed"""
        print "   " + case.how_to_behave


    def show_target(self, target):
        """Print a concrete test target as english phrase"""
        print "      " + repr(target.subject) \
                       + " " + target.meaning \
                       + " " + target.verb \
                       + " " + repr(target.object)

    def success(self, target):
        """A test target succeeded"""
        self.passed += 1

    def failure(self, target):
        """A test target failed"""
        print "FAILED:"
        self.show_target(target)
        self.failed += 1

    def finish(self):
        """The test run is done"""
        if self.failed:
            print "%s failed. %s of %s assertions passed." % (
                self.failed, self.passed, self.failed + self.passed)
        else:
            print "%s of %s assertions passed." % (self.passed, self.passed)

        self.failed = self.passed = 0

        

# ------------------------------------------------------------------------------
class Feature(object):
    """A feature under test"""

    def __init__(self, what, results):
        """Feature with short description of 'what' is being tested"""
        self.what = what
        self.results = results

    def __enter__(self):
        self.results.enter_feature(self)
        return self

    # TODO: Exception-Handling!
    def __exit__(self, *args):
        pass

    def __call__(self, how):
        return Case(self, how)

    def __repr__(self):
        return "Feature '%s'" % self.what

# ------------------------------------------------------------------------------
class Case(object):
    """A test case for a feature"""

    def __init__(self, feature, how_to_behave):
        """Test case with feature and short description 'how_to_behave' it behaves"""
        self.feature = feature
        self.results = feature.results
        self.how_to_behave = how_to_behave

    def __call__(self, target):
        return Target(self, target)

    def __enter__(self):
        self.results.enter_case(self)
        return self

    # TODO: Exception-Handling!
    def __exit__(self, *args):
        pass

# ------------------------------------------------------------------------------
class Target(object):
    """A test target over which an assertion should be made"""

    def __init__(self, case, subject, negated = False):
        """An expectation within a test 'case' concerning an subject"""
        self.case = case
        self.results = case.results
        self.subject = subject
        self.negated = negated
        self.meaning = "should not" if negated else "should"

        # set by corresponding assertion methods
        self.verb = None
        self.object = None      # the right-hand sided second argument
        self.done = False
        self.success = True     # no meaning while done = False, just optimism



    # Proxies for fluently asserting or denying the following condition
    # Example:
    #   target.should.be( ... )
    #   target.should_not.be( ... )

    def should(self):
        """Expect a statement being true"""
        return Target(self.case, self.subject, False)
    should = property(should)

    def should_not(self):
        """Expect a statement being false"""
        return Target(self.case, self.subject, True)
    should_not = property(should_not)

    def do_assertion(self, condition, verb, expected = Void):
        """Evaluates an assertion"""
        self.done = True
        self.verb = verb
        self.object = expected
        if bool(condition) ^ self.negated:
            self.results.success(self)
            self.success = True
            return True
        else:
            self.results.failure(self)
            self.success = False
            return False

    # Assertions

    def hold(self):
        self.do_assertion(self.subject, "be", True)
        return self

    def be(self, expected):
        """(==) Expects the target being equal to..."""
        self.do_assertion(self.subject == expected, "be", expected)
        return self

    def __lt__(self, expected):
        self.do_assertion(self.subject < expected, "be less than", expected)
        return self

    def __le__(self, expected):
        self.do_assertion(self.subject <= expected, "be less or equal", expected)
        return self

    def __gt__(self, expected):
        self.do_assertion(self.subject > expected, "be greater than", expected)
        return self

    def __ge__(self, expected):
        self.do_assertion(self.subject >= expected, "be greater or equal",
                          expected)
        return self

    def have(self, expected):
        """(hasattr) Expects the target having an attribute..."""
        self.do_assertion(hasattr(self.subject, expected), "have", expected)
        return self

    def contain(self, expected):
        """(in) Expects an argument being 'in' the target"""
        self.do_assertion(expected in self.subject, "contain", expected)
        return self

    def throw(self, expected):
        """Expects the target throwing the exception when evaluated"""
        thrown = False
        try:
            self.subject()
        except BaseException as e:
            thrown = isinstance(e, expected)
        self.do_assertion(thrown, "throw", expected)
        return self

    def match(self, expected):
        """Expects the target matching a regular expression"""
        self.do_assertion(re.findall(expected, self.subject), "match", expected)
        return self

    # TODO: Quantified Assertions
    #   then(lambda x: x < 1).should.hold_once_in(range(10))
    #   then(lambda x: x % 2 == 0).should.hold_in(range(1, 3))
    #   then(lambda x: x % 2 == 0).should.hold_for_all(range(0, 10, 2))
    
    
    # TODO: Differential Assertions
    #   then(x.inc).should.change(x.value).by(1)
    #   then(x.reload).should_not.change(x.value).at_all()
    #   then(lambda : x.add(pi)).should.change(x.value).by_at_least(3)
    #                                              ... .by_at_most(4)

    
# ------------------------------------------------------------------------------
# ENTRY & EXIT POINTS

# access this to change the result formatter        
main_result = TestResult()

def describe(what, result = main_result):
    """Entry point for test writing: with describe("unit") as it: ..."""
    return Feature(what, result)
                
def done(exit = True, result = main_result):
    """Finish test run and display results."""
    failures = result.failed
    result.finish()
    if exit:
        sys.exit(failures)

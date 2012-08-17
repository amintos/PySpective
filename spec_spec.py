from spec import describe, done, Target

#
# Specifies and test-runs the SPEC framework using itself
#

# ------------------------------------------------------------------------------
# Mock for verifying how the result printer is used by the test runner
# (and for avoiding STDOUT-interference with the system-under-test)

class MockResult(object):
    '''Mocks the interface used internally for reporting'''

    def enter_feature(self, feature):
        self.entered_feature = feature

    def enter_case(self, case):
        self.entered_case = case

    def success(self, target):
        self.succeeded_target = target

    def failure(self, target):
        self.failed_target = target

    def finish(self):
        self.finished = True

result = MockResult()

# ------------------------------------------------------------------------------
# Define meta-assertions over an assertion

def succeed(self):
    self.do_assertion(self.subject.done and self.subject.success, "succeed")

def fail(self):
    self.do_assertion(self.subject.done and not self.subject.success, "fail")

# Extend the Target class

Target.succeed = succeed
Target.fail = fail

# ------------------------------------------------------------------------------

with describe("A Feature") as it:

    with it("is obtained by calling 'describe'") as then:
        desc = describe("a feature", result)
        then(desc.what).should.be("a feature")

    with it("is a context handler") as then:
        then(desc).should.have('__enter__')
        then(desc).should.have('__exit__')

    with it("reports entering its with-context") as then:
        with desc:
            then(result.entered_feature).should.be(desc)

    with it("is callable") as then:
        then(callable(desc)).should.hold()

with describe("A Test Case") as it:

    with it("is obtained by calling a feature") as then:
        case = desc("behaves properly")
        then(case.how_to_behave).should.be("behaves properly")

    with it("is also a context handler") as then:
        then(case).should.have('__enter__')
        then(case).should.have('__exit__')

    with it("reports entering its with-context") as then:
        with case:
            then(result.entered_case).should.be(case)

    with it("is callable") as then:
        then(callable(desc)).should.hold()

with describe("A Test Target") as it:

    with it("is obtained by calling a test case") as then:
        target = case(42)

    with it("stores the subject") as then:
        then(target.subject).should.be(42)

    with it("generates a proxy on calling 'should'") as then:
        proxy = target.should
        then(proxy.subject).should.be(42)
        then(proxy.negated).should_not.hold()

    with it("generates a negated proxy on calling 'should_not'") as then:
        proxy = target.should_not
        then(proxy.subject).should.be(42)
        then(proxy.negated).should.hold()

    with it("does not report before any assertion") as then:
        then(result).should_not.have('succeeded_target')
        then(result).should_not.have('failed_target')

    with it("reports succeeding assertions") as then:
        target.should.be(42)
        then(result.succeeded_target.subject).should.be(42)
        then(result.succeeded_target.verb).should.be('be')
        then(result.succeeded_target.object).should.be(42)

    with it("reports failing assertions") as then:
        target.should.be(21)
        then(result.failed_target.subject).should.be(42)
        then(result.failed_target.verb).should.be('be')
        then(result.failed_target.object).should.be(21)

    with it("reports negated failing assertions as success") as then:
        target.should_not.be(21)
        then(result.succeeded_target.subject).should.be(42)
        then(result.succeeded_target.verb).should.be('be')
        then(result.succeeded_target.object).should.be(21)

with describe("A Test Target's assertions") as it:

    with it("check equality") as then:
        then(case(42).should.be(42)).should.succeed()
        then(case(42).should.be(21)).should.fail()

    with it("check less (or equal)") as then:
        then(case(42).should < 43).should.succeed()
        then(case(42).should < 42).should.fail()
        then(case(42).should <= 42).should.succeed()

    with it("check greater (or equal)") as then:
        then(case(42).should > 41).should.succeed()
        then(case(42).should > 42).should.fail()
        then(case(42).should >= 42).should.succeed()

    with it("check truth") as then:
        then(case(True).should.hold()).should.succeed()
        then(case(False).should.hold()).should.fail()

    with it("duck-type") as then:
        # beware of meta!
        then(case(then(42)).should.have('should')).should.succeed()
        then(case(then(42)).should.have('random crap')).should.fail()

    with it("find an element in a collection") as then:
        then(case([1, 2, 3]).should.contain(1)).should.succeed()
        then(case([1, 2, 3]).should.contain(4)).should.fail()

    with it("check for exceptions"):
        def epic_fail():
            raise ValueError
        then(case(epic_fail).should.throw(ValueError)).should.succeed()
        then(case(epic_fail).should.throw(MemoryError)).should.fail()

    with it("match regular expressions"):
        then(case('hello world').should.match('w.rld')).should.succeed()
        then(case('hello world').should.match('^hello$')).should.fail()

if __name__ == '__main__':
    done()


    

        
